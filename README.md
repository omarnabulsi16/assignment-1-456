How to install:

```bash
git clone https://github.com/omarnabulsi16/assignment-1-456.git
```
Choose which worm program to try: 
	- worm_one_network.py has been tested on at least one VM network.
	- worm_multiple_network.py should be capable of infecting a machine connected to more than one network

Install chosen worm*.py file to /tmp directory

-------------------------------------------------------------
How to run worm:

Run as attacker on victims
```bash
python /tmp/worm<version>.py -a
```

or

```bash
python /tmp/worm<version>.py --attack
```

How to run cleaner:

```bash
python /tmp/worm<version>.py -c
```

or

```bash
python /tmp/worm<version>.py --clean
```

