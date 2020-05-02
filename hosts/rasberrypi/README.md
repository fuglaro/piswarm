
   # Docker setup

   This installs the host image for Raspberry Pis to participate in the swarm.

   ## Raspbery Pi Swarm

   1. Get the flash tool: https://github.com/hypriot/flash
   2. Flash Hypriot with customizations (editting as appropriate):
      ```bash
      wget https://github.com/hypriot/image-builder-rpi/releases/download/v1.12.0/hypriotos-rpi-v1.12.0.img.zip -O ~/Downloads/hypriotos-rpi-v1.12.0.img.zip

      # Note: set the Wifi parameters if you need them and clear the no-wifi comment-out
      sed -e 's^PUBLICSSHRSA^'`cat ~/Private/piswarm/id_rsa.pub.key`'^g; s^DATENOW^'`date +%Y%m%d -d '+1 day'`'^g; s^WIFISSID^myWifiName^g; s^WIFIPASSWD^MYWif1P@ssw0rd^; s^#NOWIFI^^g; s^#NOHDMI^^g;' hosts/rasberrypi/userdata.yaml > ~/Private/tmp-userdata.yaml

      # Note: set the hostname
      flash --userdata ~/Private/tmp-userdata.yaml --file hosts/rasberrypi/compromised-reboot/compromised-reboot --hostname node-mach1 ~/Downloads/hypriotos-rpi-v1.12.0.img.zip
      ```
   3. Boot and ssh to the node to configure it.
      ```bash
      # Note: set the hostname.
      ssh -i ~/Private/piswarm/id_rsa chief@node-mach1.local
      ```
   4. Create USB RAID1 "storage" volume (if creating a database node):
      ```bash
      sudo apt install mdadm

      # Create fresh partition on /dev/sda and (wipes disk)
      printf "/dev/sda1 : start=2048, size=%s, type=fd\n" `expr \`sudo blockdev --getsize /dev/sda\` * 85 / 100` | sudo sfdisk --force /dev/sda

      # Create matching partition on /dev/sdb (wipes disk)
      sudo sfdisk --dump /dev/sda | sudo sfdisk --force /dev/sdb

      # Create an ext4 software RAID 1 Partition
      sudo mdadm --create /dev/md0 --level=mirror --raid-devices=2 --force /dev/sda1 /dev/sdb1
      sudo mdadm --detail --scan --verbose | sudo tee -a /etc/mdadm.conf
      sudo mkfs.ext4 /dev/md0

      # Mount the partition in the docker storage volume location
      sudo mkdir -p /data/storage
      printf '\n/dev/md0 /data/storage ext4 defaults\n' | sudo tee -a /etc/fstab
      sudo mount -a

      # Check it is running
      sudo df -h /data/storage
      sudo mdadm --detail /dev/md0
      cat /proc/mdstat
      ```

   5. Create a USB "backup" volume (if required):
      ```bash
      # Create fresh partition on /dev/sdc and (wipes disk)
      printf "/dev/sdc1 : start=1, size=%s, type=83\n" `sudo blockdev --getsize /dev/sdc` | sudo sfdisk --force /dev/sdc

      # Mount the partition in the docker backups volume location
      sudo mkdir -p /data/backups
      printf '\n/dev/sdc /data/backups ext4 defaults\n' | sudo tee -a /etc/fstab
      sudo mount -a

      # Check it is running
      sudo df -h /data/backups
      ```
   6. Configure  Gluster
      1. Set up a server pool (if required):
         1. Prepare the gluster pool (repeat on 3 hosts):
         ```bash
         # Format the USB drives
         sudo mkfs.ext4 -F -L glusterbrick1 /dev/sda1
         sudo mkdir -p /data/glusterbrick1
         printf '\n/dev/sda1 /data/glusterbrick1 ext4 defaults\n' | sudo tee -a /etc/fstab
         sudo mkfs.ext4 -F -L glusterbrick2 /dev/sdb1
         sudo mkdir -p /data/glusterbrick2
         printf '\n/dev/sdb1 /data/glusterbrick2 ext4 defaults\n' | sudo tee -a /etc/fstab
         sudo mount -a && mount

         # Create folders for a volume
         sudo mkdir /data/glusterbrick1/shared
         sudo mkdir /data/glusterbrick2/shared

         # Start the gluster server
         sudo apt install -y glusterfs-server
         sudo systemctl enable glusterd
         sudo systemctl start glusterd
         sudo service glusterd status
         ```
         2. Connect them together into a pool:
            1. From first host:
            ```bash
            # Adujst to appropriate hostnames
            sudo gluster peer probe host2
            sudo gluster peer probe host3
            ```
            2. From the second host:
            ```bash
            # Adujst to appropriate hostnames
            sudo gluster peer probe host1
            ```
            3. The third host auto connects now.

         3. Create the volume:
            ```bash
            # Adjust the hostnames as needed
            sudo gluster volume create shared replica 3 host1:/data/glusterbrick1/shared host2:/data/glusterbrick1/shared host3:/data/glusterbrick1/shared host1:/data/glusterbrick2/shared host2:/data/glusterbrick2/shared host3:/data/glusterbrick2/shared
            ```
      2. Mount the gluster volume:
         ```bash
         # Find the network gateway
         gateway=$(route -n | awk '{printf("%s\n", $2)}' | tail -n +3 | grep -v 0.0.0.0 | head -n 1)

         # Discover the gluster servers
         hosts=$(nmap --noninteractive -p24007 ${gateway}/24 -oG=- | grep /open/ | sed -e 's/.*(\([^\w]*\)).*/\1/'| paste -sd,)

         # Add the mountpoint
         sudo mkdir -p /data/shared
         printf "\ngluster,${hosts}:/shared /data/shared glusterfs defaults,_netdev\n" | sudo tee -a /etc/fstab
         sudo mount -a
         ```
   
   7. Add to the Docker Swarm.
      1. Set the node to be the first Docker Swarm Manager (if creating the first Manager):
         1. Reserve an IP address for it in the router.
         2. Run the initialisation:
         ```bash
         # Find the IP address from eth0 interface
         masterIP=`ifconfig eth0 | sed -n 's/.* inet  *\([^[:space:]]\+\).*/\1/p'`
         echo "Setting up master on ${masterIP}"

         # Initialise docker swarm
         docker swarm init --advertise-addr ${masterIP}:2377

         # Ensure join tokens get rotated daily
         cronline="0 4 * * * /usr/bin/docker swarm join-token --rotate worker; /usr/bin/docker swarm join-token --rotate manager"
         (crontab -l; echo "$cronline" ) | crontab -

         # Create the bcrswarm encrypted overlay network
         docker network create -d overlay --opt encrypted bcrswarm
         ```

      2. Add the node as another Swarm Manager (if creating other Managers):
         1. Reserve an IP address for it in the router.
         2. Run the initialisation:
         ```bash
         # Ensure join tokens get rotated daily
         cronline="0 4 * * * /usr/bin/docker swarm join-token --rotate worker; /usr/bin/docker swarm join-token --rotate manager"
         (crontab -l; echo "$cronline" ) | crontab -
         ```
         3. Find the join token from an existing master:
         ```bash
         docker swarm join-token master
         ```
         4. Add the node to the swarm with the command provided.
      3. Add the node as a worker (if creating a worker):
         1. Find the join token from an existing master:
         ```bash
         docker swarm join-token worker
         ```
         2. Add the node to the swarm with the command provided.