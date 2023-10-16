# AWS Infrastructure Deployment with Python and Boto3

This project demonstrates how to deploy AWS cloud infrastructure using Python and the Boto3 SDK. The infrastructure includes a VPC, internet gateway, public subnet, public route table, and EC2 instances.

## Prerequisites

Before running the scripts, ensure you have the following prerequisites in place:

- **AWS Account**: You need an AWS account with appropriate permissions to create VPC resources and EC2 instances.

- **Python 3**: Make sure you have Python 3.x installed on your local machine.

- **Boto3**: Install the Boto3 library by running `pip install boto3`.

## Project Structure

The project consists of the following files:

- **`create_infrastructure.py`**: Python script for creating the AWS infrastructure.

- **`README.md`**: This documentation file.

## Usage

Follow these steps to deploy the cloud infrastructure:

1. Clone the repository:

   ```bash
   git clone https://github.com/mohammadfarooqi/wecloudlearn-project1.git
   cd wecloudlearn-project1
   ```

2. Modify the script `create_aws_infra.py` to customize your infrastructure settings (e.g., instance types, security groups, etc.).

3. Run the script to create the infrastructure:

   ```bash
   python create_aws_infra.py
   ```

4. Review the console output for information about the created resources.

## Cleanup

To clean up the resources created by the script, follow these steps:

1. Open the AWS Management Console.

2. Navigate to the AWS resources created by the script (VPC, EC2 instances, etc.).

3. Delete the resources manually.

## Additional Notes

- The scripts use the `boto3` library to interact with AWS services. Make sure your AWS credentials and region are properly configured.
