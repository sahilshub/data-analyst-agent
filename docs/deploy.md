# Deploying to AWS EC2

How production works, and the one-time AWS setup behind it.

## How a deploy happens

1. A PR is merged to `main`.
2. GitHub Actions runs the checks, then builds the image and pushes it to GitHub Container Registry.
3. The `deploy` job gets temporary AWS credentials (OIDC, no stored keys) and uses
   Systems Manager (SSM) Run Command to run a short script on the instance.
4. The script downloads `deploy/compose.yaml` and `deploy/Caddyfile` for that commit,
   pulls the image tagged with the commit hash, restarts the containers and calls `/health`.

Nobody logs in to the server: there is no SSH key and port 22 is closed.

## One-time AWS setup

Do every step in the **N. Virginia (us-east-1)** region; check the region selector at the
top right of the console. Console screens change over time, so a label may differ slightly.

### 1. Role for the instance

This lets Systems Manager reach the instance.

1. IAM > Roles > Create role.
2. Trusted entity type: **AWS service**. Use case: **EC2**. Next.
3. Tick the policy **AmazonSSMManagedInstanceCore**. Next.
4. Role name: `data-analyst-agent-ec2`. Create role.

### 2. Launch the instance

1. EC2 > Instances > Launch instances.
2. Name: `data-analyst-agent`.
3. Image: **Ubuntu Server**, the current LTS release, 64-bit (x86).
4. Instance type: **t3.micro**.
5. Key pair: **Proceed without a key pair**.
6. Network settings: create a security group. **Untick** "Allow SSH traffic".
   **Tick** "Allow HTTP traffic from the internet" and "Allow HTTPS traffic from the internet".
7. Storage: 16 GiB, gp3.
8. Advanced details > IAM instance profile: `data-analyst-agent-ec2`.
9. Advanced details > User data: paste the script below. It runs once, on first boot.
10. Launch instance, then copy the **Instance ID** (it starts with `i-`).

```bash
#!/bin/bash
set -eux
# 1 GB of swap, so the 1 GB instance survives memory spikes.
fallocate -l 1G /swapfile
chmod 600 /swapfile
mkswap /swapfile
swapon /swapfile
echo '/swapfile none swap sw 0 0' >> /etc/fstab
# Docker Engine with the Compose plugin.
curl -fsSL https://get.docker.com | sh
# Where the deploy job puts the Compose file.
mkdir -p /opt/app
```

Check: after a few minutes, Systems Manager > Fleet Manager lists the instance as **Online**.

### 3. A fixed IP address

Without this, the public address changes every time the instance is stopped and started.

1. EC2 > Elastic IPs > Allocate Elastic IP address > Allocate.
2. Select it > Actions > Associate Elastic IP address > choose the instance > Associate.
3. Copy the address. The app will be at `http://<address>/health`.

Release the Elastic IP if you ever delete the instance; an unattached address is still billed.

### 4. Let GitHub Actions identify itself to AWS

1. IAM > Identity providers > Add provider.
2. Provider type: **OpenID Connect**.
3. Provider URL: `https://token.actions.githubusercontent.com`
4. Audience: `sts.amazonaws.com`. Add provider.

### 5. Role for the deploy job

1. IAM > Roles > Create role.
2. Trusted entity type: **Web identity**.
3. Identity provider: `token.actions.githubusercontent.com`. Audience: `sts.amazonaws.com`.
4. GitHub organization: `sahilshub`. Repository: `data-analyst-agent`. Branch: `main`. Next.
5. Add no policies. Next.
6. Role name: `data-analyst-agent-deploy`. Create role.
7. Open the role > Add permissions > Create inline policy > JSON. Paste the policy below,
   replacing `ACCOUNT_ID` (12 digits, shown in the top-right menu) and `INSTANCE_ID`.
8. Policy name: `deploy-via-ssm`. Create policy.
9. Copy the role's **ARN** from its summary page.

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": "ssm:SendCommand",
      "Resource": [
        "arn:aws:ec2:us-east-1:ACCOUNT_ID:instance/INSTANCE_ID",
        "arn:aws:ssm:us-east-1::document/AWS-RunShellScript"
      ]
    },
    {
      "Effect": "Allow",
      "Action": "ssm:GetCommandInvocation",
      "Resource": "*"
    }
  ]
}
```

The role can do one thing: run shell commands on this one instance, and only from the
`main` branch of this repo.

### 6. Tell the workflow where to deploy

GitHub repo > Settings > Secrets and variables > Actions > **Variables** tab > New repository variable:

| Name | Value |
| --- | --- |
| `AWS_REGION` | `us-east-1` |
| `AWS_ROLE_ARN` | the ARN from step 5 |
| `EC2_INSTANCE_ID` | the instance ID from step 2 |

These are identifiers, not secrets. Until `EC2_INSTANCE_ID` exists, the `deploy` job is skipped.

### 7. Make the image public

GitHub repo > Packages > `data-analyst-agent` > Package settings > Change visibility > Public.
The instance pulls the image without logging in, which only works for a public image.

## Turning on HTTPS later

Point a domain's DNS A record at the Elastic IP, then set `SITE_ADDRESS` to the domain
(for example in `/opt/app/.env` on the instance) and redeploy. Caddy fetches the certificate.

## Costs

The instance, its disk and its public IP address are billed by the hour, or drawn from
sign-up credits while those last. Stop the instance when you are not using it; the disk
and the Elastic IP are still billed while it is stopped.
