# Setting up a VPS

#### General Documentation
https://www.digitalocean.com/community/tutorials/an-introduction-to-securing-your-linux-vps

https://www.digitalocean.com/community/tutorials/initial-server-setup-with-debian-10

## Create instance

Setting your locale

https://wiki.debian.org/Locale


## Securing your VPS

### Ditch root user

For this, we need to create new sudo user. 

Use an original username (no admin, oracle, ubuntu...) and hard-to-guess password.

`adduser <username>`

`usermod -aG sudo <username>`

### Setup a Firewall  

Install ufw:

`sudo apt install ufw`

Set ufw rule to allow ssh only from your IP address

`sudo ufw allow (...)` 

Enable ufw:

`sudo ufw enable`

*To enable routing: check disabled(routed) from ufw status verbose*

### Hardening SSH Security

Change settings in the file `/etc/ssh/sshd_config`

#### Create password protected SSH keys

And disable simple authentication with password login.

Best setup has *password protected keys*, so even if the keys are comprimised, the attacker cannot gain access.

Use stronger encryption ed25519 instead of default RSA encryption.

Create keys on local machine with (and encrypt key with password):

`ssh-keygen -t ed25519`

Add it to the server with:

`ssh-copy-id (-i <path to key>) <user>@<host>`

#### (Change default ssh port 22 to port 1022) 

`Port 1022`

   * ports above 1024 are not for sudo only, and can cause problems if for example a user starts listening on the open port. 
   * choose a not used port (list of used ports: https://en.wikipedia.org/wiki/List_of_TCP_and_UDP_port_numbers).
   * fail2ban is setup to work with port 22. It has to be changed to work with the new port (see fail2ban section).
   * requires client side setup (`ssh -p <port> <host>`)

#### Disable root login with ssh

`PermitRootLogin no`

#### Reduce LoginGraceTime

Is how many seconds to keep connection alive while awaiting autenthication.

Change to a bit more than what you need to input the password.

`LoginGraceTime 20`

#### Reduce MaxAuthTries

`MaxAuthTries 3`

#### Enable StrictModes

Rrefuse login if authentication files have wrong permissions (e.g. can be read by other users)

`StrictModes yes`

#### Enable Key Authentication (if not already set)

`PubkeyAuthentication yes`
`ChallengeResponseAuthentication no`

#### Disable Password Authentication

*Careful! This will lock you out of your account! Follow step below first*

`PasswordAuthentication no`

#### Restart service to Set Changes

`sudo service ssh restart`

#### SSH Documentation
https://wiki.archlinux.org/index.php/SSH_keys
https://www.digitalocean.com/community/tutorials/how-to-use-ssh-to-connect-to-a-remote-server-in-ubuntu


## Set Up fail2ban

Config file for custom changes:

`/etc/fail2ban/jail.local`

In case changes were made to the default SSH port:
  * change the SSH port
  * or/and ban offending host from every port with `banaction = iptables-allports`

```
[sshd]
enabled = true
# set ssh port
port = 1022
# action (ban on all ports)
banaction = iptables-allports
# number of allowed retries
maxretry = 5
# time in seconds which should be considered for banning
findtime = 43200
# time in seconds for which the host will be banned
bantime = 2592000
# path to log with login attempts
logpath = /var/log/auth.log
```

#### fail2ban Documentation
https://www.digitalocean.com/community/tutorials/how-to-protect-ssh-with-fail2ban-on-debian-7
https://www.booleanworld.com/protecting-ssh-fail2ban/
https://serverfault.com/questions/382858/in-fail2ban-how-to-change-the-ssh-port-number

## Change passwords to secure ones

## Set Up iptables Firewall

We start with a security-first approach.

In other words, we will start by blocking all traffic, and then enabling only that what we really need.

*ATTENTION: iptables rules are by default not persistent after a reboot (pending investigation)*

Useful commands:

`iptables -S` prints all active rules

`iptables -L -v` prints all rules in the selected chain (if none is selected, prints all)

#### iptables Documentation
https://www.howtogeek.com/177621/the-beginners-guide-to-iptables-the-linux-firewall/
https://www.digitalocean.com/community/tutorials/how-to-set-up-an-iptables-firewall-to-protect-traffic-between-your-servers
http://linux-training.be/networking/ch14.html

## Set Up Openvpn

https://www.digitalocean.com/community/tutorials/how-to-set-up-an-openvpn-server-on-ubuntu-18-04


#### Log directory and Useful Logs

Location of file with authentication attempts (attempted logins):
`/var/log/auth.log`

fail2ban log:
`/var/log/fail2ban.log`

## Encrypt partition with `fscrypt`

Global setup:

`sudo fscrypt setup`

Enable fscrypt on a partition:

`fscrypt setup /mnt/<mount-point>`

Setup encryption in a directory in that partition:

`fscrypt encrypt /mnt/<mount-point>/dir1`

(in our case, as root is owner but quad is the user: `sudo fscrypt encrypt /media/encdata/clouddata --user=quad`)

### To lock and unlock acces to an encrypted directory

Lock access to the entire partition:

`sudo fscrypt purge /mnt/<mount-point>/`

(in our case, as root is owner but quad is the user: `sudo fscrypt purge /media/encdata --user=quad`)

Unlock access to a directory:

`sudo fscrypt unlock /mnt/<mount-point>/dir`

(in our case, as root is owner but quad is the user: `sudo fscrypt unlock /media/encdata/clouddata --user=quad`)

### Documentation

-https://github.com/google/fscrypt
-https://wiki.archlinux.org/index.php/Fscrypt


## Snap Nextcloud

Documentation:

-https://github.com/nextcloud/nextcloud-snap
-https://github.com/nextcloud/nextcloud-snap/wiki/Change-data-directory-to-use-another-disk-partition
-https://curius.de/blog/13-betriebssysteme/open-source/446-exkurs-nextcloud-als-snap-installieren
-https://www.digitalocean.com/community/tutorials/how-to-install-and-configure-nextcloud-on-ubuntu-18-04

## Kimsufi rescue mode

https://forum.kimsufi.com/showthread.php/35547-How-To-Rescue-Mode

## Run a command on boot

https://askubuntu.com/questions/1005986/how-to-make-some-commands-run-as-root-on-startup