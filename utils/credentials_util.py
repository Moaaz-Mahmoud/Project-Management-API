import re


class CredentialsUtil:
    @classmethod
    def is_valid_email(cls, input_str):
        """
        Check if the given input is a valid email address.

        Credits: https://www.javatpoint.com/how-to-validated-email-address-in-python-with-regular-expression

        Args:
            input_str (str): The input string to validate.

        Returns:
            bool: True if the input is a valid email address, False otherwise.
        """
        email_pattern = re.compile(r"([-!#-'*+/-9=?A-Z^-~]+(\.[-!#-'*+/-9=?A-Z^-~]+)*|\"([]!#-[^-~ \t]|(\\[\t -~]))+\")@([-!#-'*+/-9=?A-Z^-~]+(\.[-!#-'*+/-9=?A-Z^-~]+)*|\[[\t -Z^-~]*])")
        return bool(re.match(email_pattern, input_str))

    @classmethod
    def is_valid_username(cls, input_str):
        """
        Check if the given input is a valid username.

        Credits: https://stackoverflow.com/questions/12018245/regular-expression-to-validate-username

        Args:
            input_str (str): The input string to validate.

        Returns:
            bool: True if the input is a valid username, False otherwise.
        """
        # Regular expression pattern for a valid username
        username_pattern = re.compile(r'^(?=.{8,20}$)(?![_.])(?!.*[_.]{2})[a-zA-Z0-9._]+(?<![_.])$')

        # Check if the input matches the pattern
        return bool(username_pattern.match(input_str))

    @classmethod
    def get_credential_type(cls, input_str):
        """
        Determine the type of credential based on the input.

        Args:
            input_str (str): The input string.

        Returns:
            str: The type of credential ('email', 'username', or 'unknown').
        """
        if cls.is_valid_email(input_str):
            return 'email'
        elif cls.is_valid_username(input_str):
            return 'username'
        else:
            return 'unknown'
