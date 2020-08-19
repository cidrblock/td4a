import re
import sys
import traceback

class HandledException(Exception):
    def __init__(self, value):
        self.value = value
        Exception.__init__(self)

    def __str__(self):
        return repr(self.value)

    def json(self):
        return self.value['json']

class ExceptionHandler(object):
    """ Handle the expected errors."""
    def __init__(self, function):
        self.function = function
        self.error = self.typ = self.tback = self.exc_type = self.exc_value = self.exc_traceback = None
        self.error_map = {
            "requests.exceptions": self.requests_error,
            "ruamel.yaml.parser.ParserError": self.parser_error,
            "ruamel.yaml.constructor.ConstructorError": self.constructor_error,
            "ruamel.yaml.constructor.DuplicateKeyError": self.duplicate_key_error,
            "ruamel.yaml.scanner.ScannerError": self.scanner_error,
            "jinja2.exceptions": self.jinja_error,
            "TypeError": self.type_error
        }

    def __call__(self, *args, **kwargs):
        try:
            return self.function(*args, **kwargs)
        except Exception as error:
            self.error = error
            self.exc_type, self.exc_value, self.exc_traceback = sys.exc_info()
            self.tback = traceback.extract_tb(self.exc_traceback)

            error_module = getattr(error, '__module__', None)
            if error_module:
                full_error = "%s.%s" % (error.__module__, self.exc_type.__name__)
            else:
                full_error = self.exc_type.__name__
            handler = self.error_map.get(full_error,
                                         self.error_map.get(error_module,
                                                            self.unhandled))
            self.typ = kwargs.get('typ')
            message = handler()
            raise HandledException({"json": message})

    def error_response(self, message, line_number):
        error_payload = {"handled_error": {
            "in": self.typ,
            "title": "Message: Issue found loading %s." % self.typ,
            "line_number": line_number,
            "details": "Details: %s" % message,
            "raw_error": "%s\n%s" % (self.exc_type, self.exc_value)
            }
                        }
        return error_payload

    def constructor_error(self):
        line_number = self.error.problem_mark.line+1
        message = next(x for x in str(self.error).splitlines()
                       if x.startswith('found'))
        return self.error_response(message=message,
                                   line_number=line_number)

    def duplicate_key_error(self):
        line_number = self.error.problem_mark.line+1
        message = next(x for x in str(self.error).splitlines()
                       if x.startswith('found')).split('with')[0]
        return self.error_response(message=message,
                                   line_number=line_number)

    def jinja_error(self):
        message = str(self.error).replace("'ruamel.yaml.comments.CommentedMap object'", 'Object')
        line_numbers = [x for x in self.tback if re.search('^<.*>$', x[0])]
        if line_numbers:
            line_number = line_numbers[0][1]
        else:
            line_number = 'unknown'
        return self.error_response(message=message,
                                   line_number=line_number)

    def parser_error(self):
        line_number = self.error.problem_mark.line + 1
        messages = [x for x in str(self.error).splitlines() if x.startswith('expected')]
        if messages:
            message = messages[0]
        else:
            message = str(self.error)
        return self.error_response(message=message,
                                   line_number=line_number)

    def scanner_error(self):
        line_number = self.error.problem_mark.line + 1
        message = str(self.error).splitlines()[0]
        return self.error_response(message=message,
                                   line_number=line_number)

    def requests_error(self):
        message = "DB connection problems, see the browser developer tools for the full error."
        return self.error_response(message=message,
                                   line_number=None)

    def type_error(self):
        message = str(self.error)
        line_numbers = [x for x in self.tback if re.search('^<.*>$', x[0])]
        if line_numbers:
            line_number = line_numbers[0][1]
        else:
            line_number = 'unknown'
        return self.error_response(message=message,
                                   line_number=line_number)

    def unhandled(self):
        print(self.exc_type, self.exc_value, self.exc_traceback, self.tback, self.error)
        line_numbers = [x for x in self.tback if re.search('^<.*>$', x[0])]
        if line_numbers:
            line_number = line_numbers[0][1]
        else:
            line_number = None
        message = "Please see the console for details. %s" % str(self.error)
        return self.error_response(message=message,
                                   line_number=line_number)
