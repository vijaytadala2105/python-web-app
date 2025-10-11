from aws_cdk import (
    Stack,
    aws_ec2 as ec2,
    aws_ecs as ecs,
    aws_ecs_patterns as ecs_patterns,
    aws_iam as iam,
    aws_ecr as ecr,
    Tags,
)
from constructs import Construct

class EcsStackStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

          # VPC
        # vpc = ec2.Vpc.from_lookup(self, "VPC", vpc_id="vpc-05c1e7c9dfe69c69a") # Replace with your VPC ID
        vpc = ec2.Vpc(self, "pocvpc",
            max_azs=2,
            nat_gateways=1,
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    name="Public",
                    subnet_type=ec2.SubnetType.PUBLIC,
                    cidr_mask=24
                ),
                ec2.SubnetConfiguration(
                    name="Private",
                    subnet_type=ec2.SubnetType.PRIVATE_WITH_NAT,
                    cidr_mask=24
                )
            ]
        )

        # Cluster
        cluster = ecs.Cluster(self, "MyCluster", vpc=vpc)

        execution_role = iam.Role(self, "ExecutionRole",
            assumed_by=iam.ServicePrincipal("ecs-tasks.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AmazonECSTaskExecutionRolePolicy")
            ]
        )
        repo = ecr.Repository.from_repository_name(self, "PRIVATEREPO", "poc")
        image=ecs.ContainerImage.from_ecr_repository(repo, tag="latest")

        # Security Group for Fargate Tasks
        fargate_sg = ec2.SecurityGroup(self, "FargateSG",
            vpc=vpc,
            description="Security group for ECS Fargate tasks",
            allow_all_outbound=True
        )
        
        # Security Group for Load Balancer
        alb_sg = ec2.SecurityGroup(self, "ALBSG",
            vpc=vpc,
            description="Security group for ALB",
            allow_all_outbound=True
        )
        
        # Allow ALB to talk to Fargate tasks on container port
        fargate_sg.add_ingress_rule(
            peer=alb_sg,
            connection=ec2.Port.tcp(8000),
            description="Allow ALB to reach Fargate container"
        )
        
        # Allow public HTTP access to ALB (port 80)
        alb_sg.add_ingress_rule(
            peer=ec2.Peer.any_ipv4(),
            connection=ec2.Port.tcp(80),
            description="Allow public HTTP traffic to ALB"
        )


        service = ecs_patterns.ApplicationLoadBalancedFargateService(
            self,
            "MyFargateService",
            cluster=cluster,
            cpu=256,
            memory_limit_mib=512,
            desired_count=2,
            public_load_balancer=True,
            task_subnets=ec2.SubnetSelection(
                subnet_type=ec2.SubnetType.PRIVATE_WITH_NAT
            ),
            security_groups=[fargate_sg],
            task_image_options=ecs_patterns.ApplicationLoadBalancedTaskImageOptions(
                image=image,
                container_port=8000,
                execution_role=execution_role
            )
        )
        service.service.circuit_breaker = ecs.DeploymentCircuitBreaker(rollback=True)
        service.service.deployment_controller = ecs.DeploymentController(
            type=ecs.DeploymentControllerType.ECS
        )
        service.load_balancer.connections.security_groups.clear()
        service.load_balancer.connections.security_groups.append(alb_sg)


        Tags.of(service).add("Project", "MyProject")
        Tags.of(service).add("Environment", "Production")
        Tags.of(service).add("Owner", "MyTeam")
        Tags.of(service).add("CostCenter", "12345")
        Tags.of(service).add("Application", "MyApp")
        Tags.of(service).add("Department", "IT")
