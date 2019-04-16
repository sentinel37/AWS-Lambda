print("You will have to create a security group to apply traffic on both port 22 and 8080\n")



SecurityGroupID=input("Please enter Security Group ID: ")
print("\n")
Subnet=input("Please enter Subnet ID: ")
print("\n")
Region=input("Please enter Region: ")
print("\n")
InstanceType=input("Please enter Instance type: ")
print("\n")
ServerName=input("Enter Server Name: ")
print("\n")


saveFile = open ('Lambda-Job.py','w')
saveFile.write("""

#Lambda to launch Jenkins Server with Lambda
import boto3

REGION = '"""+Region+"""' # region to launch instance.
AMI = 'ami-0080e4c5bc078760e'
    # matching region/setup amazon linux ami, as per:
    # https://aws.amazon.com/amazon-linux-ami/
INSTANCE_TYPE = '"""+InstanceType+"""' # instance type to launch.
Subnet='"""+Subnet+"""'
Security='"""+SecurityGroupID+"""'



EC2 = boto3.client('ec2', region_name=REGION)

def lambda_handler(event, context):


    # bash script to run:
    #  - update and install httpd (a webserver)
    #  - start the webserver
    #  - create a webpage with the provided message.
    #  - set to shutdown the instance in 5 minutes.
    
    
    init_script = \"""#!/bin/bash
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
\"""

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
    tagger = EC2.create_tags(Resources=[instance_id], Tags=[{'Key':'Name', 'Value':'"""+ServerName+"""'}])
    print (instance_id)
    print("To Learn how to access your Jenkins Service, follow the link below ")
    print("https://docs.aws.amazon.com/aws-technical-content/latest/jenkins-on-aws/installation.html")
    return instance_id


""")
saveFile.close()

saveFile = open ('Instructions.txt','w')
saveFile.write("""
Navigate to IAM Console and create a new role with:
   - EC2 Full Access
   - CloudWatch Full Access

   
Navigate to the AWS Lambda Console
Select Create Function
Select Author from Scratch
Enter a name for your Lambda function
Select Create Function
Select Python 3.7 for Runtime
Under Execution Role: Select the the IAM Lambda IAM role
Select Create Function

Paste the Contents of Lambda-Job.py into the Function Code section


At the top of the screen, Select Test.
Enter an event name
Select Save
Select Test

SSH into """+ServerName+"""
Copy the output from 'cat /var/lib/jenkins/secrets/initialAdminPassword'
In your web browser, navigate to 'http://<ip address>:8080' and enter the initialAdminPassword from the previous step
Follow the remaining on-screen directions.


Additional guidance from be located at:
https://docs.aws.amazon.com/aws-technical-content/latest/jenkins-on-aws/installation.html
""")
saveFile.close()


print("Open Instructions.txt for directions on running the Lambda Job.")
