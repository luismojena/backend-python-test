from flask import g


class MessageType:
    Error = 1
    Information = 2


def add_validation_message(message):
    g.messages.append({'text': message, 'type': MessageType.Error})


def add_information_message(message):
    g.messages.append({'text': message, 'type': MessageType.Information})


class validators:
    """
    All functions in this class return a tuple containing two values
    in the following form.
    >>> valid, message = validate_not_empty('abc')

    valid - Specifies if the value to be validated results valid,
    in which case the returned value will be True and False otherwise

    message - Holds a message to be displayed if the value passed in
    is not valid. If the value is valid returns None.

    """

    @staticmethod
    def validate_not_empty(value):
        message = 'Required field with empty value.'
        if value is not None:
            if value.strip() != '':
                return True, None
            else:
                return False, message
        else:
            return False, message

    @staticmethod
    def validate_not_empty_field(value, field):
        message = 'Required field: \'%s\' with empty value.' % field
        if value is not None:
            if value.strip() != '':
                return True
            else:
                return False, message
        else:
            return False, message
