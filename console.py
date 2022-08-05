#!/usr/bin/python3

"""
A module that defines the command line interpreter for AirBnB project
"""

import re
import cmd
import json
import shlex
from models import storage
from models.user import User
from models.base_model import BaseModel


class HBNBCommand(cmd.Cmd):
    """
    Entry point of the command line interpreter
    """
    prompt = '(hbnb) '
    __classes = {
        'BaseModel': BaseModel,
        'User': User
    }

    def parseline(self, line):
        """Parse the line into a command name and a string containing
        the arguments.  Returns a tuple containing (command, args, line).
        'command' and 'args' may be None if the line couldn't be parsed.
        """
        line = self.__parseline(line)
        return super().parseline(line)

    def do_create(self, arg):
        """Creates an instance of `BaseModel`
        Usage: create BaseModel
        """
        args = shlex.split(arg)
        self.__validateArgs('create', args)
        if len(args) > 0 and args[0] in self.__classes:
            newBaseModel = self.__classes[args[0]]
            new = newBaseModel()
            storage.save()
            print(new.id)

    def do_show(self, arg):
        """
        Shows string representation of a class id given

        Attr:
            arg (str): string of arguments
        """
        args = shlex.split(arg)
        result = self.__validateArgs('show', args)
        if type(result) == list:
            [objs, key] = result
            print(objs.get(key, ''))

    def do_destroy(self, arg):
        """
        Deletes an instance based on the class name and id

        Attr:
            arg (str): string of arguments
        """
        args = shlex.split(arg)
        result = self.__validateArgs('destroy', args)
        if type(result) == list:
            [objs, key] = result
            objs.pop(key, None)
            storage.save()

    def __all(self, arg):
        """
        Prints all string representation of
        all instances based or not on the class name

        Attr:
            arg (str): string or arguments
        """
        args = shlex.split(arg)
        model = None
        if len(args) > 0:
            if not (self.__classes.get(args[0], None)):
                return print('** class doesn\'t exist **')
            model = args[0]
        obList = [str(v) for v in (storage.all()).values()]
        if model:
            match = '[{}]'.format(model)
            obList = list(filter(lambda s: s.startswith(match), obList))
        return (obList)

    def do_all(self, arg):
        """
        Prints all instances
        """
        hall = self.__all(arg)
        if hall is not None:
            print(hall)

    def do_count(self, arg):
        """
        Returns count of a given model
        """
        count = self.__all(arg)
        if count is not None:
            print(len(count))

    def __updateMePlease(self, obj, args):
        """
        Checks if update inputs are valid

        Attr:
            obj (BaseModel): instance to be updated
            args (list): list of passed arguments

        Return:
            (str): error message
            (None): if no parameters are valid and all set
        """
        args = (args).replace("'", '"')
        params = json.loads(args)
        for key, value in params.items():
            if key == "None":
                return print('** attribute name missing **')
            if value == "None":
                return print('** value missing **')
            setattr(obj, key, value)
        obj.save()

    def do_update(self, arg):
        """
        Updates an instance based on the class name and id by adding or
        updating attribute

        Attr:
            arg (str): string or arguments
        """
        args = shlex.split(arg)
        result = self.__validateArgs('update', args)
        if type(result) != list:
            return
        [objs, key] = result
        newargs = args + ['None', 'None', 'None']
        [three, four] = newargs[2:4]
        if three.startswith('{') and three.endswith('}'):
            newargs[2] = three
        else:
            four = four if four.isnumeric() else '"{}"'.format(four)
            newargs[2] = '{"' + three + '": ' + four + '}'
        obj = objs.get(key, None)
        self.__updateMePlease(obj, newargs[2])

    def do_quit(self, arg):
        """Quit command to exit the program
        """
        return True

    def do_EOF(self, arg):
        """Exits the interpreter
        """
        return True

    def __validateArgs(self, query, args):
        """
        Validates given parameters

        Attr:
            query (str): action to be performed
            args (list): list of parameters

        Return:
            None: on valid inputs
            (str): on invalid inputs
        """
        actions = ['create', 'destroy', 'show', 'update']
        if len(args) < 1:
            return print('** class name missing **')
        if not (self.__classes.get(args[0], None)):
            return print('** class doesn\'t exist **')
        if query in actions[1:]:
            if len(args) < 2:
                return print('** instance id missing **')
            key = '.'.join(args[:2])
            objs = storage.all()
            if objs.get(key, None):
                return [objs, key]
            return print('** no instance found **')
        return None

    def __parseline(self, line):
        """
        Parse command formats like `<Model>.<action>(<*args>)`
        to native formats
        """
        newLine = line.strip()
        args = re.search(r'\(.*?\)', newLine)
        if args is not None:
            params = args.group().strip('()')
            curls = re.search(r'\{(.*?)\}', params)
            if curls:
                items = curls.group()
                try:
                    uid = shlex.split(params[:curls.span()[0]])[0].strip(",")
                except IndexError:
                    uid = ""
                newargs = '{} \'{}\''.format(uid, items.replace("'", '"'))
            else:
                newargs = params.split(',')
                newargs = " ".join(newargs) or ""
            action = shlex.split(newLine[:args.span()[0]])[0].split(".")
            if len(action) == 2:
                line = "{} {} {}".format(action[1], action[0], newargs.strip())
        return line


if __name__ == '__main__':
    HBNBCommand().cmdloop()
