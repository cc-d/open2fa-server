from fastapi import HTTPException


class NoUserFoundException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=404,
            detail="No user found for the given X-User-Hash header",
        )


class NoUserHashException(HTTPException):
    def __init__(self):
        super().__init__(status_code=400, detail="Missing X-User-Hash header")


class TOTPExistsException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=409,
            detail="TOTP with given encrypted secret already exists for user",
        )


class NoTOTPFoundException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=404,
            detail="No TOTP found for the given user with this enc_secret",
        )
