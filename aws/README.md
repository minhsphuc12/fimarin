# AWS Setup and Usage Guide

## Installation and Setup

1. Install AWS SDK (Boto3):
   ```
   pip install boto3
   ```

2. Configure AWS CLI:
   ```
   aws configure
   ```
   Enter your AWS Access Key ID, Secret Access Key, and default region. You can obtain these credentials from the AWS Management Console:

   1. Log in to the AWS Management Console (https://console.aws.amazon.com/)
   2. Click on your account name in the top right corner
   3. Select "Security credentials"
   4. Under "Access keys", click "Create New Access Key"
   5. Download and securely store the key file
   6. Use the Access Key ID and Secret Access Key from this file when configuring AWS CLI

   For the default region, choose the AWS region closest to you or where you plan to deploy your resources (e.g., us-west-2, eu-west-1).

3. Import CloudFormation template:
   ```
   aws cloudformation create-stack --stack-name my-newsletter-stack --template-body file:///Users/phucnm/git/misc/test_llm/fimarin/aws/news_workflow_infrastructure.yml --capabilities CAPABILITY_NAMED_IAM

   ```

## Monitoring and Management

1. Monitor CloudFormation stack:
   - AWS Console: CloudFormation > Stacks > my-newsletter-stack
   - CLI: `aws cloudformation describe-stacks --stack-name my-newsletter-stack`

2. Monitor Lambda functions:
   - AWS Console: Lambda > Functions
   - CloudWatch Logs: CloudWatch > Log groups > /aws/lambda/[function-name]

3. Check DynamoDB data:
   - AWS Console: DynamoDB > Tables > [your-table-name] > Items
   - CLI: `aws dynamodb scan --table-name [your-table-name]`

4. View generated newsletters:
   - S3 Console: S3 > [your-bucket-name] > weekly_newsletter_*.md
   - CLI: `aws s3 ls s3://[your-bucket-name]/weekly_newsletter_`

5. Access served newsletters:
   - Web browser: https://[your-api-gateway-url]/prod/newsletter?name=[newsletter-filename]
   - API Gateway Console: API Gateway > [your-api-name] > Stages > prod

Remember to replace placeholders (e.g., [your-table-name], [your-bucket-name]) with your actual resource names.
