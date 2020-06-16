import boto3
import click

session = boto3.Session(profile_name='snapshots')
ec2 = session.resource('ec2')

def filter_instances(instances, project):
    if project:
        filters = [{'Name':'tag:Project', 'Values':[project]}]
        instances = instances.filter(Filters=filters)

    return instances

@click.group()
def cli():
    """Snapshots manages EC2 snapshots"""

@cli.group('instances')
def instances():
    """Commands for instances"""

@instances.command('start')
@click.option('--project', default=None,
    help="Only instances for project (tag Project:<name>)")
def start_instances(project):
    "Start EC2 instances"
    instances = filter_instances(ec2.instances.all(), project)

    for i in instances:
        print("Starting {0}...".format(i.id))
        i.start()

@instances.command('stop')
@click.option('--project', default=None,
    help="Only instances for project (tag Project:<name>)")
def stop_instances(project):
    "Stop EC2 instances"
    instances = filter_instances(ec2.instances.all(), project)

    for i in instances:
        print("Stopping {0}...".format(i.id))
        i.stop()

@instances.command('snapshot')
@click.option('--project', default=None,
    help="Only instances for project (tag Project:<name>)")
def create_snapshots(project):
    "Create snapshots of ec2 instance volumes"
    instances = filter_instances(ec2.instances.all(), project)

    for i in instances:
        print("Stopping {0}...".format(i.id))

        i.stop()
        i.wait_until_stopped()

        for v in i.volumes.all():
            print("Creating snapshot of {0}".format(v.id))
            v.create_snapshot(Description="Created by Snapshots script")

        print("Starting {0}...".format(i.id))

        i.start()
        i.wait_until_running()

    print("Job's done!")

    return

@instances.command('list')
@click.option('--project', default=None,
    help="Only instances for project (tag Project:<name>)")
def list_instances(project):
    "List EC2 instances"
    instances = filter_instances(ec2.instances.all(), project)

    for i in instances:
        tags = { t['Key']: t['Value'] for t in i.tags or [] }
        print(', '.join((
            i.id,
            i.instance_type,
            i.placement['AvailabilityZone'],
            i.state['Name'],
            i.public_dns_name,
            tags.get('Project', '<no_project>'))))

    return

@cli.group('volumes')
def volumes():
    """Commands for volumes"""

@volumes.command('list')
@click.option('--project', default=None,
    help="Only volumes for instances in project (tag Project:<name>)")
@click.option('--instance', default=None,
    help="Only volumes for a specific instance (use instance ID)")
def list_volumes(project, instance):
    "List EC2 volumes"
    if instance:
        ids = [instance]
        instances = ec2.instances.filter(InstanceIds=ids)
        for i in instances:
            for v in i.volumes.all():
                print(', '.join((
                    v.id,
                    i.id,
                    v.state,
                    str(v.size) + "GiB",
                    v.encrypted and "Encrypted" or "Not Encrypted")))

        return

    instances = filter_instances(ec2.instances.all(), project)

    for i in instances:
        for v in i.volumes.all():
            print(', '.join((
                v.id,
                i.id,
                v.state,
                str(v.size) + "GiB",
                v.encrypted and "Encrypted" or "Not Encrypted")))

    return

@cli.group('snapshots')
def snapshots():
    """Commands for snapshots"""

@snapshots.command('list')
@click.option('--project', default=None,
    help="Only snapshots for instances in project (tag Project:<name>)")
@click.option('--instance', default=None,
    help="Only snapshots for a specific instance (use instance ID)")
def list_snapshots(project, instance):
    "List EC2 volume snapshots"
    if instance:
        ids = [instance]
        instances = ec2.instances.filter(InstanceIds=ids)
        for i in instances:
            for v in i.volumes.all():
                for s in v.snapshots.all():
                    print(', '.join((
                        s.id,
                        v.id,
                        i.id,
                        s.state,
                        s.progress,
                        s.start_time.strftime("%c"))))

        return

    instances = filter_instances(ec2.instances.all(), project)

    for i in instances:
        for v in i.volumes.all():
            for s in v.snapshots.all():
                print(', '.join((
                    s.id,
                    v.id,
                    i.id,
                    s.state,
                    s.progress,
                    s.start_time.strftime("%c"))))

    return

if __name__ == '__main__':
    cli()
