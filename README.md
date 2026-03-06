# SC4PS - Homework 1

This guide explains how to create a Linux Virtual Machine on CloudVeneto and configure it to compile and run C programs.

## 1. Access the CloudVeneto Dashboard

Login to the CloudVeneto dashboard:

https://cloudveneto.ict.unipd.it/dashboard

## 2. Create an SSH Key Pair

1. Go to **Project → Compute → Key Pairs**
2. Click **Create Key Pair**
3. Give the key a name (example: `my_hey`)
4. Download the `.pem` file

Move the key to a safe location and set the correct permissions:

```bash
chmod 600 my_key.pem
```

## 3. Launch a Linux Virtual Machine

1. Go to **Project → Compute → Instances**
2. Click **Launch Instance**
3. Configure the instance with the following parameters:

- **Instance Name:** VM-Linux
- **Image:** AlmaLinux or Ubuntu
- **Flavor:** cloudveneto.large
- **Key Pair:** select your key
- **Network:** `<ProjectName>-lan`

4. Click **Launch Instance**

After a few seconds the VM will start and you will see its **IP address**.

---

## 4. Access the Gate Machine

If you are outside the university network, connect first to the gate server:

```bash
ssh username@gate.cloudveneto.it
```

## 5. Copy the SSH Key to the Gate Machine

From your local computer:

```bash
scp my_key.pem username@gate.cloudveneto.it:~
```

Then organize the key:

```bash
mkdir ~/private
mv ~/my_key.pem ~/private/
chmod 600 ~/private/my_key.pem
```

## 6. Connect to Your Virtual Machine

Use the VM private IP address.

For **AlmaLinux instances**:

```bash
ssh -i ~/private/my_key.pem almalinux@VM_IP
```

## 7. Install the C Compiler

On AlmaLinux install GCC:

```bash
sudo dnf install gcc
```

Check the installation:

```bash
gcc --version
```

## 8. Compile and Run a C Program

Create a simple C program:

```bash
nano hello.c
```

Example code:

```c
#include <stdio.h>

int main() {
    printf("Hello, CloudVeneto!\n");
    return 0;
