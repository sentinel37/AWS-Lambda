""" Lambda to launch ec2-instances """
import boto3

REGION = 'us-east-1' # region to launch instance.
AMI = 'ami-0080e4c5bc078760e'
    # matching region/setup amazon linux ami, as per:
    # https://aws.amazon.com/amazon-linux-ami/
INSTANCE_TYPE = 'm3.medium' # instance type to launch.
Subnet='subnet-09418927a570c2c5f'
Security='sg-0638ac1a9dbbde7b8'

#interface = boto.ec2.networkinterface.NetworkInterfaceSpecification(subnet_id='subnet-09418927a570c2c5f',
#                                                                    groups=['sg-0638ac1a9dbbde7b8'],
#                                                                    associate_public_ip_address=True)


EC2 = boto3.client('ec2', region_name=REGION)

def lambda_to_ec2(event, context):


    # bash script to run:
    #  - update and install httpd (a webserver)
    #  - start the webserver
    #  - create a webpage with the provided message.
    #  - set to shutdown the instance in 5 minutes.
    
    
    init_script = """#!/bin/bash
sudo wget -O /etc/yum.repos.d/jenkins.repo http://pkg.jenkins.io/redhat/jenkins.repo
sudo rpm --import https://pkg.jenkins.io/redhat/jenkins.io.key
sudo yum install jenkins -y
sudo yum install -y java-1.8.0-openjdk.x86_64
sudo /usr/sbin/alternatives --set java /usr/lib/jvm/jre-1.8.0-openjdk.x86_64/bin/java
sudo /usr/sbin/alternatives --set javac /usr/lib/jvm/jre-1.8.0-openjdk.x86_64/bin/javac
sudo yum remove java-1.7
sudo chkconfig jenkins on
sudo service jenkins start
sudo yum -y update
#shutdown -h +2
"""

    print ('Running script:')
    print (init_script)

    instance = EC2.run_instances(
        ImageId=AMI,
        #SubnetId=Subnet,
        InstanceType=INSTANCE_TYPE,
        MinCount=1, # required by boto, even though it's kinda obvious.
        MaxCount=1,
        KeyName="Learning",
        InstanceInitiatedShutdownBehavior='terminate', # make shutdown in script terminate ec2
        UserData=init_script, # file to run on instance init.

        NetworkInterfaces=[{
            "DeviceIndex": 0,
            "SubnetId": Subnet,
            "AssociatePublicIpAddress": True
        }]
        
    )

    print ("New instance created.")
    instance_id = instance['Instances'][0]['InstanceId']
    tagger = EC2.create_tags(Resources=[instance_id], Tags=[{'Key':'Name', 'Value':'Jenkins Test Man'}])
    print (instance_id)
    print("To Learn how to access your Jenkins Service, follow the link below ")
    print("https://docs.aws.amazon.com/aws-technical-content/latest/jenkins-on-aws/installation.html")
    return instance_id
