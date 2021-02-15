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
    Subnet,
    Vpc,
    VpnGatewayAttachment,
)

tagger = Tagger(environment_name="dev")

vpc = Vpc(
    resource_name="airflow",
    cidr_block="192.168.0.0/16",
    enable_dns_support=True,
    enable_dns_hostnames=True,
    tags=tagger.create_tags("airflow"),
)

internetGateway = InternetGateway(
    resource_name="airflow", tags=tagger.create_tags("airflow")
)

internetGatewayAttachment = VpnGatewayAttachment(
    resource_name="airflow", vpc_id=vpc.id, vpn_gateway_id=internetGateway.id
)

publicSubnet1 = Subnet(
    resource_name="airflow-public-eu-west-1a",
    availability_zone="eu-west-1a",
    cidr_block="192.168.0.0/24",
    map_public_ip_on_launch=True,
    vpc_id=vpc.id,
    tags=tagger.create_tags(
        "airflow-public-eu-west-1a",
    ),
)

publicSubnet2 = Subnet(
    resource_name="airflow-public-eu-west-1b",
    availability_zone="eu-west-1b",
    cidr_block="192.168.1.0/24",
    map_public_ip_on_launch=True,
    vpc_id=vpc.id,
    tags=tagger.create_tags(
        "airflow-public-eu-west-1b",
    ),
)

privateSubnet1 = Subnet(
    resource_name="airflow-private-eu-west-1a",
    availability_zone="eu-west-1a",
    cidr_block="192.168.2.0/24",
    map_public_ip_on_launch=True,
    vpc_id=vpc.id,
    tags=tagger.create_tags(
        "airflow-private-eu-west-1a",
    ),
)

privateSubnet2 = Subnet(
    resource_name="airflow-private-eu-west-1b",
    availability_zone="eu-west-1b",
    cidr_block="192.168.3.0/24",
    map_public_ip_on_launch=True,
    vpc_id=vpc.id,
    tags=tagger.create_tags(
        "airflow-private-eu-west-1b",
    ),
)

natGatewayEip1 = Eip(
    resource_name="airflow-eu-west-1a",
    vpc=True,
    tags=tagger.create_tags("airflow-eu-west-1a"),
    opts=ResourceOptions(depends_on=[internetGateway]),
)

natGatewayEip2 = Eip(
    resource_name="airflow-eu-west-1b",
    vpc=True,
    tags=tagger.create_tags("airflow-eu-west-1b"),
    opts=ResourceOptions(depends_on=[internetGateway]),
)

natGateway1 = NatGateway(
    resource_name="airflow-eu-west-1a",
    allocation_id=natGatewayEip1.allocation_id,
    subnet_id=publicSubnet1.id,
    tags=tagger.create_tags("airflow-eu-west-1a"),
)

natGateway2 = NatGateway(
    resource_name="airflow-eu-west-1b",
    allocation_id=natGatewayEip2.allocation_id,
    subnet_id=publicSubnet2.id,
    tags=tagger.create_tags("airflow-eu-west-1b"),
)

publicRouteTable = RouteTable(
    resource_name="airflow-public", vpc_id=vpc.id, tags=tagger.create_tags("airflow")
)

defaultPublicRoute = Route(
    resource_name="airflow-public",
    destination_cidr_block="0.0.0.0/0",
    gateway_id=internetGateway.id,
    route_table_id=publicRouteTable.id,
)

publicRouteTableAssociation1 = RouteTableAssociation(
    resource_name="airflow-public-eu-west-1a",
    route_table_id=publicRouteTable.id,
    subnet_id=publicSubnet1.id,
)

publicRouteTableAssociation2 = RouteTableAssociation(
    resource_name="airflow-public-eu-west-1b",
    route_table_id=publicRouteTable.id,
    subnet_id=publicSubnet2.id,
)

privateRouteTable1 = RouteTable(
    resource_name="airflow-private-eu-west-1a",
    vpc_id=vpc.id,
    tags=tagger.create_tags("airflow-private-eu-west-1a"),
)

defaultPrivateRoute1 = Route(
    resource_name="airflow-private-eu-west-1a",
    destination_cidr_block="0.0.0.0/0",
    nat_gateway_id=natGateway1.id,
    route_table_id=privateRouteTable1.id,
)

privateRouteTableAssociation1 = RouteTableAssociation(
    resource_name="airflow-private-eu-west-1a",
    route_table_id=privateRouteTable1.id,
    subnet_id=privateSubnet1.id,
)

privateRouteTable2 = RouteTable(
    resource_name="airflow-private-eu-west-1b",
    vpc_id=vpc.id,
    tags=tagger.create_tags("airflow-private-eu-west-1b"),
)

defaultPrivateRoute2 = Route(
    resource_name="airflow-private-eu-west-1b",
    destination_cidr_block="0.0.0.0/0",
    nat_gateway_id=natGateway2.id,
    route_table_id=privateRouteTable2.id,
)

privateRouteTableAssociation2 = RouteTableAssociation(
    resource_name="airflow-private-eu-west-1b",
    route_table_id=privateRouteTable2.id,
    subnet_id=privateSubnet2.id,
)

securityGroup = SecurityGroup(resource_name="airflow", name="airflow", vpc_id=vpc.id)
