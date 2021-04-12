from dataengineeringutils3.pulumi import Tagger
from pulumi import ResourceOptions
from pulumi_aws.ec2 import (
    Eip,
    InternetGateway,
    NatGateway,
    Route,
    RouteTable,
    RouteTableAssociation,
    SecurityGroup,
    SecurityGroupRule,
    Subnet,
    Vpc,
)
from pulumi_aws import get_availability_zones

tagger = Tagger(environment_name="dev")

available = get_availability_zones(state="available")

vpc = Vpc(
    resource_name="airflow",
    cidr_block="10.192.0.0/16",
    enable_dns_support=True,
    enable_dns_hostnames=True,
    tags=tagger.create_tags("airflow"),
)

internetGateway = InternetGateway(
    resource_name="airflow",
    tags=tagger.create_tags("airflow"),
    vpc_id=vpc.id,
    opts=ResourceOptions(parent=vpc),
)

publicSubnet1 = Subnet(
    resource_name="airflow-public-eu-west-1a",
    availability_zone=available.names[0],
    cidr_block="10.192.10.0/24",
    map_public_ip_on_launch=True,
    vpc_id=vpc.id,
    tags=tagger.create_tags(
        "airflow-public-eu-west-1a",
    ),
    opts=ResourceOptions(parent=vpc),
)

publicSubnet2 = Subnet(
    resource_name="airflow-public-eu-west-1b",
    availability_zone=available.names[1],
    cidr_block="10.192.11.0/24",
    map_public_ip_on_launch=True,
    vpc_id=vpc.id,
    tags=tagger.create_tags(
        "airflow-public-eu-west-1b",
    ),
    opts=ResourceOptions(parent=vpc),
)

privateSubnet1 = Subnet(
    resource_name="airflow-private-eu-west-1a",
    availability_zone=available.names[0],
    cidr_block="10.192.20.0/24",
    map_public_ip_on_launch=False,
    vpc_id=vpc.id,
    tags=tagger.create_tags(
        "airflow-private-eu-west-1a",
    ),
    opts=ResourceOptions(parent=vpc),
)

privateSubnet2 = Subnet(
    resource_name="airflow-private-eu-west-1b",
    availability_zone=available.names[1],
    cidr_block="10.192.21.0/24",
    map_public_ip_on_launch=False,
    vpc_id=vpc.id,
    tags=tagger.create_tags(
        "airflow-private-eu-west-1b",
    ),
    opts=ResourceOptions(parent=vpc),
)

natGatewayEip1 = Eip(
    resource_name="airflow-eu-west-1a",
    vpc=True,
    tags=tagger.create_tags("airflow-eu-west-1a"),
    opts=ResourceOptions(depends_on=[internetGateway], parent=internetGateway),
)

natGatewayEip2 = Eip(
    resource_name="airflow-eu-west-1b",
    vpc=True,
    tags=tagger.create_tags("airflow-eu-west-1b"),
    opts=ResourceOptions(depends_on=[internetGateway], parent=internetGateway),
)

natGateway1 = NatGateway(
    resource_name="airflow-eu-west-1a",
    allocation_id=natGatewayEip1.id,
    subnet_id=publicSubnet1.id,
    tags=tagger.create_tags("airflow-eu-west-1a"),
    opts=ResourceOptions(parent=publicSubnet1),
)

natGateway2 = NatGateway(
    resource_name="airflow-eu-west-1b",
    allocation_id=natGatewayEip2.id,
    subnet_id=publicSubnet2.id,
    tags=tagger.create_tags("airflow-eu-west-1b"),
    opts=ResourceOptions(parent=publicSubnet2),
)

publicRouteTable = RouteTable(
    resource_name="airflow-public",
    vpc_id=vpc.id,
    tags=tagger.create_tags("airflow"),
    opts=ResourceOptions(parent=vpc),
)

defaultPublicRoute = Route(
    resource_name="airflow-public",
    destination_cidr_block="0.0.0.0/0",
    gateway_id=internetGateway.id,
    route_table_id=publicRouteTable.id,
    opts=ResourceOptions(parent=publicRouteTable),
)

publicRouteTableAssociation1 = RouteTableAssociation(
    resource_name="airflow-public-eu-west-1a",
    route_table_id=publicRouteTable.id,
    subnet_id=publicSubnet1.id,
    opts=ResourceOptions(parent=publicRouteTable),
)

publicRouteTableAssociation2 = RouteTableAssociation(
    resource_name="airflow-public-eu-west-1b",
    route_table_id=publicRouteTable.id,
    subnet_id=publicSubnet2.id,
    opts=ResourceOptions(parent=publicRouteTable),
)

privateRouteTable1 = RouteTable(
    resource_name="airflow-private-eu-west-1a",
    vpc_id=vpc.id,
    tags=tagger.create_tags("airflow-private-eu-west-1a"),
    opts=ResourceOptions(parent=vpc),
)

defaultPrivateRoute1 = Route(
    resource_name="airflow-private-eu-west-1a",
    destination_cidr_block="0.0.0.0/0",
    nat_gateway_id=natGateway1.id,
    route_table_id=privateRouteTable1.id,
    opts=ResourceOptions(parent=privateRouteTable1),
)

privateRouteTableAssociation1 = RouteTableAssociation(
    resource_name="airflow-private-eu-west-1a",
    route_table_id=privateRouteTable1.id,
    subnet_id=privateSubnet1.id,
    opts=ResourceOptions(parent=privateRouteTable1),
)

privateRouteTable2 = RouteTable(
    resource_name="airflow-private-eu-west-1b",
    vpc_id=vpc.id,
    tags=tagger.create_tags("airflow-private-eu-west-1b"),
    opts=ResourceOptions(parent=vpc),
)

defaultPrivateRoute2 = Route(
    resource_name="airflow-private-eu-west-1b",
    destination_cidr_block="0.0.0.0/0",
    nat_gateway_id=natGateway2.id,
    route_table_id=privateRouteTable2.id,
    opts=ResourceOptions(parent=privateRouteTable2),
)

privateRouteTableAssociation2 = RouteTableAssociation(
    resource_name="airflow-private-eu-west-1b",
    route_table_id=privateRouteTable2.id,
    subnet_id=privateSubnet2.id,
    opts=ResourceOptions(parent=privateRouteTable2),
)

securityGroup = SecurityGroup(
    resource_name="airflow",
    name="airflow",
    vpc_id=vpc.id,
    opts=ResourceOptions(parent=vpc),
)

ingressRule = SecurityGroupRule(
    resource_name="ingress",
    from_port=0,
    protocol="all",
    security_group_id=securityGroup.id,
    source_security_group_id=securityGroup.id,
    to_port=65535,
    type="ingress",
)

egressRule = SecurityGroupRule(
    resource_name="egress",
    cidr_blocks=["0.0.0.0/0"],
    from_port=0,
    protocol="all",
    security_group_id=securityGroup.id,
    to_port=65535,
    type="egress",
)
