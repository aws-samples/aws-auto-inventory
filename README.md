<!--

  ** DO NOT EDIT THIS FILE
  ** 
  ** This file was automatically generated by the [CLENCLI](https://github.com/awslabs/clencli)
  ** 1) Make all changes on files under clencli/yaml/*.yaml
  ** 2) Run `clencli template` to rebuild this file
  **
  ** By following this practice we ensure standard and high-quality accross multiple projects.
  ** DO NOT EDIT THIS FILE

-->

![logo](https://images.unsplash.com/photo-1546198632-9ef6368bef12?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=MXwxOTEyNTB8MHwxfGFsbHx8fHx8fHx8&ixlib=rb-1.2.1&q=80&w=1080)



# AWS Automated Inventory  ( aws-auto-inventory ) 

Automates creation of detailed inventories from AWS resources.

## Table of Contents
---




 - [Usage](#usage) 

 - [Installing](#installing) 
 - [Testing](#testing) 


 - [Contributors](#contributors) 
 - [References](#references) 
 - [License](#license) 
 - [Copyright](#copyright) 


## Screenshots
---
<details open>
  <summary>Expand</summary>


| ![how-to-run](clencli/terminalizer/run.gif) |
|:--:| 
| *How to run* |

| ![ec2-inventory-result](clencli/media/ec2-inventory-result.png) |
|:--:| 
| *EC2 Inventory Result* |

</details>



## Usage
---
<details open>
  <summary>Expand</summary>

```
aws-auto-inventory --help
usage: aws-auto-inventory [-h] --name NAME

Automates creation of detailed inventories from AWS resources.

optional arguments:
  -h, --help            show this help message and exit
  --name NAME, -n NAME  inventory name
```
### Problem
Projects usually have several resources and fetching all the information manually is a very time-consuming task.
This issue is intensified when the same project have multiple environments, e.g.: NonProd, QA and/or Prod.

### Solution
Provide a simple way to fetch the required information and generate a spreadsheet.
The information can be filtered, e.g. filter results by tag:x, vpc, subnets, etc.
</details>





## Installing
---
<details open>
  <summary>Expand</summary>

Download the binary according to your operating system and platform. After you can execute it directly.
You will need to create a `config.yaml` file in order to tell the tool how to generate your inventory, here are the default search paths for each platform:

* OS X: `~/.config/aws-auto-inventory/config.yaml` or  `~/Library/Application Support/aws-auto-inventory/config.yaml`
* Other Unix: `$XDG_CONFIG_HOME/aws-auto-inventory/config.yaml` or  `~/.config/aws-auto-inventory/config.yaml`
* Windows: `%APPDATA%\aws-auto-inventory\config.yaml` where the `APPDATA` environment variable falls back to `%HOME%\AppData\Roaming\config.yaml` if undefined

You can use the [config-sample](config-sample.yaml) as an example. A snippet can be found below:
```
inventories:
  - name: your-inventory-name
    aws:
      profile: your-aws-profile
      region:
        - us-east-1
    excel:
      transpose: true
    sheets:
      - name: EC2 # sheet name on Excel
        service: ec2 # the boto3 client of an AWS service
        function: describe_instances # the client method of the service defined above
        result_key: Reservations # [optional]: The first key of the response dict
      - name: EBS
        service: ec2
        function: describe_volumes
        result_key: Volumes
```
</details>



## Testing
---
<details>
  <summary>Expand</summary>

AWS-Auto-Inventory uses [boto3](https://github.com/boto/boto3).
You can use any service that contains any list or describe method to fetch information about your resources.

### Parameters
You can use [boto3](https://github.com/boto/boto3) parameters to narrow down your search results.

#### Filter by tag:Name

```
sheets:
  - name: VPC
    service: ec2
    function: describe_vpcs
    result_key: Vpcs
    parameters:
      Filters:
        - Name: tag:Name
          Values:
            - my-vpc
```

### Filter by vpc-id

```
sheets:
  - name: Subnets
    service: ec2
    function: describe_subnets
    result_key: Subnets
    parameters:
      Filters:
        - Name: vpc-id
          Values:
            - vpc-xxx
```

### Find a particular RDS instance

```
sheets:
  - name: RDS
    service: rds
    function: describe_db_instances
    result_key: DBInstances
    parameters:
      DBInstanceIdentifier: the-name-of-my-rds-instance
```

### Find EC2 instances by a particular tag

```
sheets:
  - name: EC2
    service: ec2
    function: describe_instances
    result_key: Reservations
    parameters:
      Filters:
        - Name: tag:ApplicationName
          Values:
            - my-application
```

### Find a particular IAM Role
```
sheets:
  - name: IAM.Role
    service: iam
    function: get_role
    result_key: Role
    parameters:
      RoleName: my-role
```
</details>







## Contributors
---
<details open>
  <summary>Expand</summary>

|     Name     |         Email        |       Role      |
|:------------:|:--------------------:|:---------------:|
|  Silva, Valter  |  valterh@amazon.com  |  AWS Professional Services - Cloud Architect  |

</details>





## References
---
<details open>
  <summary>Expand</summary>

  * [clencli](https://github.com/awslabs/clencli) - Cloud Engineer CLI
  * [boto3](https://github.com/boto/boto3) - Boto3


</details>



## License
---
This project is licensed under the Apache License 2.0.



## Copyright
---
```
Amazon, Inc. or its affiliates. All Rights Reserved.
```

