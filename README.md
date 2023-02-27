
![Enery Management System](https://user-images.githubusercontent.com/60348643/172327364-418797ce-912d-4269-8c3f-c22a4d3a4022.png)

# Distributed Energy Resource Management System (DERMS)


## Requirements:
Requirement         | Specification
------------------- | --------------------------------------
OS                  | Ubuntu 18.04 or higher
Language            | Python
Interpreter         | Python 3.8+

## Local Development QuickStart:
### - Using docker-compose:

Dependencies:

- `docker` and `docker-compose`

    ```bash
    # install
    $ git clone https://github.com/tiss-co/derms.git
    $ cd derms

    # configure (the defaults are fine for development)
    $ edit `.env.sample` and save as `.env`

    # run it
    $ docker-compose up --build
    ```

    Once it's done building and everything has booted up:

    - Access the app at: [http://localhost:8088](http://localhost:8088)

### - Running locally

- Dependencies:
    - Linux system
    - Python 3.8+
    - Your virtualenv tool of choice (poetry or virtualenv)
    - PostgreSQL or MariaDB (MySQL)
    - Redis (used for sessions persistence and scheduling jobs)
- Installation
    ```bash
    # install
    $ git clone https://github.com/tiss-co/derms.git
    $ cd derms
    $ virtualenv -p /path/to/python3 venv
    $ source venv/bin/activate
    $ pip install -r requirements.txt

    # configure
    $ edit `.env.sample` and save as `.env`

    # run db migrations
    $ flask db upgrade head

    # backend dev server:
    $ flask run
    ```

## API references
- After running `derms` service, you can import the derms postman API collection in the postman directory at the root of the project and call the APIs by setting the desired variables.
