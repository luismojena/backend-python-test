from flask import g


def add_validation_message(message):
    g.validation_errors.append(message)
    g.validation_dirty = True


class validators:

    @staticmethod
    def validate_not_empty(value):
        if value is not None:
            if value.strip() != '':
                return value
            else:
                add_validation_message('Required field with empty value.')
                return None
        else:
            add_validation_message('Required field with empty value.')
            return None

    @staticmethod
    def validate_not_empty_field(value, field):
        if value is not None:
            if value.strip() != '':
                return value
            else:
                add_validation_message('Required field: \'%s\' with empty value.' % field)
                return None
        else:
            add_validation_message('Required field: \'%s\' with empty value.' % field)
            return None
