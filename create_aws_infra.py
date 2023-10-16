import boto3


def create_vpc():
    ec2_client = boto3.client("ec2", region_name="us-east-1")
    vpc = ec2_client.create_vpc(CidrBlock="10.0.0.0/16")
    vpc_id = vpc["Vpc"]["VpcId"]

    # Add tags to the VPC
    ec2_client.create_tags(
        Resources=[vpc_id], Tags=[{"Key": "project", "Value": "wecloud"}, {"Key": "Name", "Value": "wecloud-proj-1-vpc"}]
    )

    print(f"VPC created: {vpc}")
    print(f"VPC created with ID: {vpc_id}")
    return vpc_id


def create_internet_gateway(vpc_id):
    ec2_client = boto3.client('ec2', region_name='us-east-1')
    igw = ec2_client.create_internet_gateway()
    igw_id = igw['InternetGateway']['InternetGatewayId']

    # Attach the internet gateway to the VPC
    ec2_client.attach_internet_gateway(VpcId=vpc_id, InternetGatewayId=igw_id)

    # Add tags to the internet gateway
    ec2_client.create_tags(Resources=[igw_id], Tags=[{'Key': 'project', 'Value': 'wecloud'}, {"Key": "Name", "Value": "wecloud-proj-1-igw"}])

    print(f"Internet Gateway created: {igw}")
    print(f"Internet Gateway created with ID: {igw_id}")
    return igw_id


def create_route_to_igw(vpc_id, igw_id):
    ec2_client = boto3.client('ec2', region_name='us-east-1')

    # Get the default route table ID for the VPC
    default_route_table_id = get_default_route_table_id(vpc_id)

    if default_route_table_id:
        # Create a route to the internet gateway in the default route table
        ec2_client.create_route(RouteTableId=default_route_table_id, DestinationCidrBlock='0.0.0.0/0', GatewayId=igw_id)
        print(f"Added route to the internet gateway in the default route table ({default_route_table_id})")
    else:
        print("No default route table found for the VPC. Creating a custom route table.")
        create_route_table(vpc_id, igw_id)

    return default_route_table_id


def create_subnet(vpc_id):
    ec2_client = boto3.client("ec2", region_name="us-east-1")
    subnet = ec2_client.create_subnet(
        VpcId=vpc_id, CidrBlock="10.0.0.0/24", AvailabilityZone="us-east-1a"
    )
    subnet_id = subnet["Subnet"]["SubnetId"]

    # Add tags to the subnet
    ec2_client.create_tags(
        Resources=[subnet_id], Tags=[{"Key": "project", "Value": "wecloud"}, {"Key": "Name", "Value": "wecloud-proj-1-subnet"}]
    )

    ec2_client.modify_subnet_attribute(
        SubnetId=subnet_id, MapPublicIpOnLaunch={"Value": True}
    )

    print(f"Subnet created: {subnet}")
    print(f"Subnet created with ID: {subnet_id}")
    return subnet_id


def get_default_route_table_id(vpc_id):
    ec2_client = boto3.client('ec2', region_name='us-east-1')
    route_tables = ec2_client.describe_route_tables(Filters=[{'Name': 'vpc-id', 'Values': [vpc_id]}])['RouteTables']

    print(f"route_tables {route_tables}")

    for table in route_tables:
        associations = [association.get('Main', False) for association in table.get('Associations', [])]
        print(f"Associations for {table['RouteTableId']}: {associations}")
        if True == associations[0]:
            print(f"Found 'Main' in associations for table['RouteTableId']: {table['RouteTableId']}")
            return table['RouteTableId']

    return None



def create_route_table(vpc_id, igw_id):
    ec2_client = boto3.client("ec2", region_name="us-east-1")
    route_table = ec2_client.create_route_table(VpcId=vpc_id)
    route_table_id = route_table["RouteTable"]["RouteTableId"]

    # Add tags to the route table
    ec2_client.create_tags(
        Resources=[route_table_id], Tags=[{"Key": "project", "Value": "wecloud"}, {"Key": "Name", "Value": "wecloud-proj-1-rt"}]
    )

    ec2_client.create_route(
        RouteTableId=route_table_id, DestinationCidrBlock="0.0.0.0/0", GatewayId=igw_id
    )
    print(f"Route Table: {route_table}")
    print(f"Route Table created with ID: {route_table_id}")
    return route_table_id


def create_ec2_instance(instance_params, name = "wecloud-proj-1-ec2"):
    ec2_client = boto3.client("ec2", region_name="us-east-1")
    response = ec2_client.run_instances(**instance_params)
    instance_id = response["Instances"][0]["InstanceId"]

    # Add tags to the EC2 instance
    ec2_client.create_tags(
        Resources=[instance_id], Tags=[{"Key": "project", "Value": "wecloud"}, {"Key": "Name", "Value": name}]
    )

    print(f"EC2 Instance created with ID: {instance_id}")
    return instance_id


def create_security_group(vpc_id):
    ec2_client = boto3.client('ec2', region_name='us-east-1')
    response = ec2_client.create_security_group(
        GroupName='wecloud-sg-1',
        Description='Proj 1 sg',
        VpcId=vpc_id
    )
    security_group_id = response['GroupId']

    # Define inbound rules for SSH access
    ec2_client.authorize_security_group_ingress(
        GroupId=security_group_id,
        IpPermissions=[
            {
                'IpProtocol': 'tcp',
                'FromPort': 22,
                'ToPort': 22,
                'IpRanges': [{'CidrIp': '0.0.0.0/0'}]  # Allow SSH access from anywhere (for demonstration purposes)
            },
        ]
    )

    print(f"Security Group created with ID: {security_group_id}")
    return security_group_id


def main():
    vpc_id = create_vpc()
    igw_id = create_internet_gateway(vpc_id)
    subnet_id = create_subnet(vpc_id)
    # route_table_id = create_route_table(vpc_id, igw_id)
    route_table_id = create_route_to_igw(vpc_id, igw_id)
    security_group_id = create_security_group(vpc_id)


    # Define instance parameters
    instance_params = {
        "SecurityGroupIds": [security_group_id],
        "MaxCount": 1,
        "MinCount": 1,
        "ImageId": "ami-0261755bbcb8c4a84",  # Ubuntu 20.04 AMI ID
        "InstanceType": "t2.small",
        "KeyName": "aws_devops",  # Replace with your SSH key pair
        "SubnetId": subnet_id,
        # "TagSpecifications": [
        #     {
        #         "ResourceType": "instance",
        #         "Tags": [{"Key": "project", "Value": "wecloud"}],
        #     }
        # ],
        "UserData": """
            #!/bin/bash -ex
            exec > >(tee /var/log/user-data.log|logger -t user-data -s 2>/dev/console) 2>&1
            echo BEGIN
            date '+%Y-%m-%d %H:%M:%S'

            sudo apt update
            sudo apt upgrade

            # Install python 3.10
            sudo apt install -y build-essential zlib1g-dev libncurses5-dev libgdbm-dev libnss3-dev libssl-dev libsqlite3-dev libreadline-dev libffi-dev wget libbz2-dev

            wget https://www.python.org/ftp/python/3.10.0/Python-3.10.0.tgz

            tar -xf Python-3.10.0.tgz

            cd Python-3.10.0

            ./configure - enable-optimizations

            make -j$(nproc)
            sudo make altinstall

            python3.10 - version

            # cleanup
            cd ..
            rm -rf Python-3.10.0
            rm Python-3.10.0.tgz

            # Install Node 18
            sudo apt install -y curl

            curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -

            sudo apt install -y nodejs

            node --version

            # Install Java 11
            sudo apt-get install openjdk-11-jdk

            java -version
            javac -version

            # Install Docker
            sudo apt-get install ca-certificates curl gnupg
            sudo install -m 0755 -d /etc/apt/keyrings
            curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
            sudo chmod a+r /etc/apt/keyrings/docker.gpg

            echo \
                "deb [arch="$(dpkg --print-architecture)" signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
                "$(. /etc/os-release && echo "$VERSION_CODENAME")" stable" | \
                sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

            sudo apt-get update

            sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

            sudo docker images

            echo END
        """,
    }

    master_node_id = create_ec2_instance(instance_params, "master-node-01")

    instance_params["InstanceType"] = "t2.micro"
    worker1_node_id = create_ec2_instance(instance_params, "worker-node-01")
    worker2_node_id = create_ec2_instance(instance_params, "worker-node-02")




if __name__ == "__main__":
    main()
