# open2fa-server

[open2fa.liberfy.ai](https://open2fa.liberfy.ai) NOW LIVE

[open2fa client](https://github.com/cc-d/open2fa)

This is the code for the webui/api enabling the remote capabilities of the open2fa client.

## Security

The Frontend Javascript has been kept to absolute minimum for security reasons, and is implemented entirely in VanillaJS without any 3rd party libraries or frameworks. All the frontend code is in `nginx/html/js/index.js`. That being said, if you have serious security concerns, you should not be generating 2FA codes using the webui, and should instead use the open2fa client exclusively.

## How it works

See: [open2fa.liberfy.ai](https://open2fa.liberfy.ai)

![how it works](/sync.png)

## Installation

First, clone the repository:

```bash
git clone https://github.com/cc-d/open2fa.git
```

Then, create a virtual environment and install the dependencies:

```bash
cd open2fa
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Usage

To run the server, simply execute:

```bash
./uvicorn.sh
```

### Docker

To run the server using Docker, simply execute:

```bash
docker-compose build
docker-compose up
```

And then navigate to `http://localhost:80` in your web browser.

## Testing

To run the tests, simply execute:

```bash
./run_tests.sh
```
