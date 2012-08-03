import boto.ec2
import requests
import time
import ssh
from nobleman import Person, db
from serf_settings import *

conn = None
client = None

def create(username, region='us-west-2'):
    make_connection(region)
    instance = create_instance()
    if instance is None:
        print "Something failed!"
        return

    status = []
    status.append(connect_ssh(instance.public_dns_name))
    status.append(update_twoface())
    status.append(create_new_user(username))
    
    if [False, None] in status:
        terminate_instance(instance)
        tstatus = 'errored'
    else:
        stop_instance(instance)
        tstatus = 'completed'
        
    add_person(username, instance.id)
    
    payload = {
            'username': username,
            'instance': instance.id,
            'dns_name': instance.public_dns_name,
            'state': tstatus,
    }

    try:
        requests.post(KING_URL+"/command/"+str(id), data=payload)
    except Exception as e:
        print e
        print payload


def add_person(username, instance_id, password='password'):
    p = Person(username=username, instance_id=instance_id, password=password)
    db.session.add(p)
    db.session.commit()


def kill(username):
    make_connection()
    p = Person.query.filter_by(username=username).first()
    terminate_instance(p.instance_id)

    db.session.delete(p)
    db.session.commit()


def upvote(username, title, region='us-west-2'):
    p = Person.query.filter_by(username=username).first()

    make_connection(region)
    instance = start_instance(p.instance_id)

    connect_ssh(instance.public_dns_name)
    update_twoface()
    perform_upvote(username=p.username, password=p.password, title=title)

    stop_instance(instance)


def make_connection(region='us-west-2'):
    regions = boto.ec2.regions(aws_access_key_id=AWS_ACCESS_KEY_ID, 
                    aws_secret_access_key=AWS_SECRET_ACCESS_KEY)

    for r in regions:
        if region in r.name:
            global conn
            conn = r.connect(aws_access_key_id=AWS_ACCESS_KEY_ID, 
                    aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
            break
    else:
        print "No matching region found"
        return

    return conn


def create_instance():
    reservation = conn.run_instances(AMI_IMAGE_ID, key_name=AWS_KEY_PAIR_NAME,
            security_group_ids=[AWS_SECURITY_GROUP_ID],
            instance_type='t1.micro')

    instance = reservation.instances[0]

    while instance.state != 'running':
        print 'Waiting on instance start...'
        time.sleep(10)
        instance.update()
    
    time.sleep(90)
    
    return instance


def start_instance(instance_id):
    instance = conn.start_instances([instance_id])[0]

    while instance.state != 'running':
        time.sleep(10)
        instance.update()
        print "Waiting for instance to start..."

    time.sleep(90)

    return instance


def stop_instance(instance):
    conn.stop_instances([instance.id])

    while instance.state != 'stopped':
        print 'Waiting on instance stop...'
        time.sleep(10)
        instance.update()


def terminate_instance(instance):
    if type(instance) == str or unicode:
        id = instance
    else:
        id = instance.id

    instance = conn.terminate_instances([id])[0]

    while instance.state != 'terminated':
        print 'Waiting on instance termination...'
        time.sleep(10)
        instance.update()

def connect_ssh(url):
    c = ssh.SSHClient()
    privkey = ssh.RSAKey.from_private_key_file(KEY_FILE)
    c.set_missing_host_key_policy(ssh.AutoAddPolicy())

    try:
        c.connect(url, username='ubuntu', pkey=privkey)
        global client
        client = c
    except Exception as e:
        print e
        return


def update_twoface():
    exec_string = 'cd /opt/two-face/ && sudo git pull'
    stdin, stdout, stderr = client.exec_command(exec_string)
    print "s: "+stdout.read()
    print "e: "+stderr.read()


def create_new_user(username):
    exec_string = 'casperjs --username=%s /opt/two-face/actions/new_user.js' % username
    stdin, stdout, stderr = client.exec_command(exec_string)

    print "s: "+stdout.read()
    print "e: "+stderr.read()


def perform_upvote(username, password, title):
    if title == '':
        exec_string = 'casperjs --username=%s --password=%s /opt/two-face/actions/upvote.js' % (username, password)

    else:
        title = title.decode('UTF-8')
        exec_string = 'casperjs --title="%s" --username=%s --password=%s /opt/two-face/actions/upvote.js' % (title, username, password)
    
    stdin, stdout, stderr = client.exec_command(exec_string)

    print "s: "+stdout.read()
    print "e: "+stderr.read()

