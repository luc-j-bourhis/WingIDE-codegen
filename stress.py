class Something(object):
  
  
  def __init__(self, arg, another_arg, yet_another_arg, *args, **kwds):
    """ Constructor """
    self.arg = arg
    self.another_arg = another_arg
    self.yet_another_arg = yet_another_arg


  def some_method(self, more_arg, more_and_more_arg, so_much_more_args):
    self.more_and_more_arg = more_and_more_arg
    self.more_arg = more_arg
    self.so_much_more_args = so_much_more_args


  def some_other_method(self, fancy_arg, crazy_arg):
    self.mad_arg = mad_arg # existing code: select and execute command

def some_func(arg_one, arg_two):
  """ Some function """
  
