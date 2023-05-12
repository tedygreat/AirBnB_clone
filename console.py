#!/usr/bin/python3
"""Defines the HBnB console."""
import cmd
import re
from shlex import split
import sys
import json
import os
from shlex import split
from models import storage
from models.base_model import BaseModel
from models.user import User
from models.place import Place
from models.state import State
from models.city import City
from models.amenity import Amenity
from models.review import Review

def parse(arg):
    curly_braces = re.search(r"\{(.*?)\}", arg)
    brackets = re.search(r"\[(.*?)\]", arg)
    if curly_braces is None:
        if brackets is None:
            return [i.strip(",") for i in split(arg)]
        else:
            lexer = split(arg[:brackets.span()[0]])
            retl = [i.strip(",") for i in lexer]
            retl.append(brackets.group())
            return retl
    else:
        lexer = split(arg[:curly_braces.span()[0]])
        retl = [i.strip(",") for i in lexer]
        retl.append(curly_braces.group())
        return retl

class HBNBCommand(cmd.Cmd):
    """ General Class for HBNBCommand """
    prompt = '(hbnb) '
    classes = {'BaseModel': BaseModel, 'User': User, 'City': City,
               'Place': Place, 'Amenity': Amenity, 'Review': Review,
               'State': State}

    def do_quit(self, arg):
        """ Quit command to exit the program."""
        exit()

    def do_EOF(self, arg):
        """  """
        print('')
        exit()

    def emptyline(self):
        """ Method to pass when emptyline entered """
        pass

    def default(self, arg):
        """Default behavior for cmd module when input is invalid"""
        argdict = {
            "all": self.do_all,
            "show": self.do_show,
            "destroy": self.do_destroy,
            "count": self.do_count,
            "update": self.do_update
        }
        match = re.search(r"\.", arg)
        if match is not None:
            argl = [arg[:match.span()[0]], arg[match.span()[1]:]]
            match = re.search(r"\((.*?)\)", argl[1])
            if match is not None:
                command = [argl[1][:match.span()[0]], match.group()[1:-1]]
                if command[0] in argdict.keys():
                    call = "{} {}".format(argl[0], command[1])
                    return argdict[command[0]](call)
        print("*** Unknown syntax: {}".format(arg))
        return False


    def do_create(self, arg):
        """ Create a new instance """
        if len(arg) == 0:
            print('** class name missing **')
            return
        new = None
        if arg:
            arg_list = arg.split()
            if len(arg_list) == 1:
                if arg in self.classes.keys():
                    new = self.classes[arg]()
                    new.save()
                    print(new.id)
                else:
                    print("** class doesn't exist **")

    def do_show(self, arg):
        """ Method to print instance 
        Usage: show <class> <id> or <class>.show(<id>)"""
        argl = arg.split()
        if len(argl) == 0:
            print('** class name missing **')
            return
        elif argl[0] not in self.classes:
            print("** class doesn't exist **")
            return
        elif len(argl)  == 1:
            print('** instance id missing **')
        elif len(argl) > 1:
            key = argl[0] + '.' + argl[1]
            if key in storage.all():
                i = storage.all()
                print(i[key])
            else:
                print('** no instance found **')

    def do_destroy(self, arg):
        """ Method to delete instance with class and id """
        arg_list = arg.split()
        objdict = storage.all()
        if len(arg) == 0:
            print("** class name missing **")
            return
        elif arg_list[0] not in self.classes:
            print("** class doesn't exist **")
            return
        elif len(arg_list) == 1:
            print('** instance id missing **')
            return
        elif "{}.{}".format(arg_list[0], arg_list[1]) not in objdict.keys():
            print('** no instance found **')
        else:
            del objdict["{}.{}".format(arg_list[0], arg_list[1])]
            storage.save()

           
    def do_all(self, arg):
        """ Method to print all instances """
        arg1 = arg.split()
        if len(arg1) > 0 and arg1[0] not in self.classes:
            print("** class doesn't exist **")
        else:
            obj1 = []
            for obj in storage.all().values():
                if len(arg1) == 0:
                    objl.append(obj.__str__())
                elif len(arg1) > 0 and  arg1[0] == obj.__class__.__name__:
                    obj1.append(obj.__str__())
            print(obj1)

    def do_update(self, arg):
        """ Method to update JSON file update 
        <class> <id> <attribute_name> <attribute_value> or
       <class>.update(<id>, <attribute_name>, <attribute_value>) or
       <class>.update(<id>, <dictionary>)"""
        arg = arg.split()
        objdic = storage.all()
        if len(arg) == 0:
            print('** class name missing **')
            return
        elif arg[0] not in self.classes:
            print("** class doesn't exist **")
            return
        elif len(arg) == 1:
            print('** instance id missing **')
            return
        elif len(arg) == 2:
            print("** attribute name missing **")
            return
        elif "{}.{}".format(arg[0], arg[1]) not in objdic.keys():
            print("** no instance found **")
            return
        elif len(arg) == 3:
            try:
                type(eval(argl[2])) != dict
            except NameError:
                print("** value missing **")
                return False

        if len(arg) == 4:
            obj = objdic["{}.{}".format(arg[0], arg[1])]
            if arg[2] in obj.__class__.__dict__.keys():
                valtype = type(obj.__class__.__dict__[arg[2]])
                obj.__dict__[arg[2]] = valtype(arg[3])
            else:
                obj.__dict__[arg[2]] = arg[3]
        elif type(eval(arg[2])) == dict:
            obj = objdict["{}.{}".format(arg[0], arg[1])]
            for k, v in eval(arg[2]).items():
                if (k in obj.__class__.__dict__.keys() and
                        type(obj.__class__.__dict__[k]) in {str, int, float}):
                    valtype = type(obj.__class__.__dict__[k])
                    obj.__dict__[k] = valtype(v)
                else:
                    obj.__dict__[k] = v
        storage.save()


    def do_count(self, arg):
        """Usage: count <class> or <class>.count()
        Retrieve the number of instances of a given class."""
        argl =  arg.split()
        count = 0
        if len(argl) == 0:
            print ("** class name missing **")
            return
        if len(argl) > 0 and argl[0] not in self.classes:
            print("** class doesn't exist **")
        else:
            for obj in storage.all().values():
                if len(argl) > 0 and argl[0] == obj.__class__.__name__:
                   count += 1
                elif len(argl) == 0:
                    print("** class doesn't exist **")
            print(count)


if __name__ == '__main__':
    HBNBCommand().cmdloop()
