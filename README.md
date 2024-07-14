# AWS Image AutoResizer (Python)

To run this project locally on MacOS / Linux, refer to [README.default.md](./README.default.md) or use:

### Step 1 - One-off setup (locally)

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt 
```

### Step 2 - One-off CDK Bootstrap in your AWS Account 

```bash
cdk bootstrap
```

Expected output:

```
 ⏳  Bootstrapping environment aws://<AWS_ACCOUNT_ID>/us-east-1...
Trusted accounts for deployment: (none)
Trusted accounts for lookup: (none)
Using default execution policy of 'arn:aws:iam::aws:policy/AdministratorAccess'. Pass '--cloudformation-execution-policies' to customize.
CDKToolkit: creating CloudFormation changeset...
 ✅  Environment aws://<AWS_ACCOUNT_ID>/us-east-1 bootstrapped.
```

### Step 3 - Application Deployment

```bash
cdk synth
cdk deploy --all
```