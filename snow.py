from typeclasses.objects import Object
from evennia import CmdSet
from evennia import TICKER_HANDLER as tickerhandler
from commands.command import MuxCommand
from evennia.commands.command import InterruptCommand
from evennia.utils import logger, search
from evennia.server.sessionhandler import SESSIONS

import traceback
import time
import random

class CmdSnow(MuxCommand):
      key = 'snow'
      locks = 'cmd:perm(builder)'
      help_category = 'Winter'
      options = ('on', 'off')

      def parse(self):
          super().parse()

      @property
      def active(self):
          return self.obj.attributes.get('active', False)

      @active.setter
      def active(self, val):
          self.obj.attributes.add('active', val)

      def func(self):
          opt = self.switches

          if 'on' in opt and not self.active:
             self.character.location.msg_contents(text="A festive fanfare plays and snow swirls!")
             self.active = True
             self.obj.cmdset.add('typeclasses.snow.SnowActiveCmdSet', permanent=True)
             tickerhandler.add(interval=900, callback=self.obj.snowOn, idstring=f'snowticker-{self.obj.dbref}', persistent=True, snowpile=self.obj)
          elif 'off' in opt and self.active:
             self.character.location.msg_contents(text="The music stops suddenly and suddenly there's no snow at all..")
             self.active = False
             self.obj.cmdset.remove('typeclasses.snow.SnowActiveCmdSet')

             try:
                tickerhandler.remove(interval=900, callback=self.obj.snowOn, idstring=f'snowticker-{self.obj.dbref}', persistent=True)
             except:
                logger.log_info(f'CMDSNOW EX2 {repr(traceback.print_exc())}')
          elif 'on' in opt and self.active:
             self.character.msg('Snow is already falling!')
          elif 'off' in opt and not self.active:
             self.character.msg('Snow has already stopped!')
          else:
             self.character.msg(f'The snow is{" not " if not self.active else " "}falling.')
           
          return

class CmdMakeSnowAngel(MuxCommand):
      key = 'make snow angel'
      locks = 'cmd:all()'
      help_category = 'Winter'

      def parse(self):
         super().parse()
   
      def func(self):
          char = self.character

          if not char.attributes.has('messages'): 
             char.attributes.add('messages', {})

          char.db.messages['pose'] = ' is making Snow Angels.'
          char.execute_cmd('pose sprawls out in the snow and makes a |wS|Wn|Co|ww |wAn|yg|Ye|wl.')

class CmdHideInSnow(MuxCommand):
      key = 'hide in snow'
      locks = 'cmd:all()'
      help_category = 'Winter'

      def parse(self):
         super().parse()
   
      def func(self):
          char = self.character

          if not char.attributes.has('messages'): 
             char.attributes.add('messages', {})

          char.db.messages['pose'] = ' is hiding in the snow.'
          char.execute_cmd('pose burrows into the snowbank and hides!')

class CmdGatherSnow(MuxCommand):
      key = 'gather snow'
      locks = 'cmd:all()'
      help_category = 'Winter'
      
      def parse(self):
          super().parse()

      def func(self):
          now = time.time()

          if self.character.attributes.has('lastgather') and now - self.character.attributes.get('lastgather') < 60:
             self.character.msg(f"You've gathered snow too recently yet.")
             return
          
          self.character.attributes.add('lastgather', now)
          self.character.attributes.add('snowballs', 3)
          self.character.execute_cmd('pose gathers up some snowballs.')

class CmdTossSnow(MuxCommand):
      key = 'toss snow'
      locks = 'cmd:all()'
      help_category = 'Winter'
      
      def parse(self):
          super().parse()

          try:
             if self.args.strip().lower().startswith('at '):
                self.target = search.search_object(self.args.strip().lower()[3:], 
                                                   typeclass='typeclasses.characters.Character', 
                                                   use_dbref=True, candidates=self.character.location.contents)
                
                if self.target:
                   self.target = self.target[0]
                else:
                   self.character.msg('|rUsage: |Ytoss snow at <player>|w')
                   raise InterruptCommand
             else: 
                self.character.msg('|rUsage: |Ytoss snow at <player>|w')
                raise InterruptCommand
          except:
                logger.log_info(f'CTS {traceback.print_exc()}')
                raise InterruptCommand

      def func(self):
          now = time.time()

          if not self.character.attributes.has('snowballs'):
             self.character.msg(f"You need to gather snow.")
             return
          elif self.character.attributes.get('snowballs') < 1:
             self.character.msg(f"You need to gather snow.")
             return
          elif not self.target:
             self.character.msg(f"Invalid target!")
             return
          elif self.character.attributes.has('lastsnowtoss') and now - self.character.attributes.get('lastsnowtoss') < 10:
             self.character.msg(f"You've tossed a snowball too recently yet.")
             return
          
          self.character.attributes.add('snowballs', self.character.attributes.get('snowballs') - 1)

          snowskill = 8

#          try:
#             if self.character.attributes.has('snowskill'):
#                snowskill = int(self.character.attributes.get('snowskill'))
#          except:
#             pass

          toss = random.choice(range(max(1, snowskill)))

          modifier = 0
          modifier_text = ''

          try:
             if self.target.attributes.has('lastsnowtoss'):
                if self.target.attributes.get('lastsnowtoss') + 15 > time.time():
                   modifier = 1
                   modifier_text = ' out in the open'
 
          except:
             pass
       
          toss += modifier

          target_name = self.target.get_display_name(self.character)	

          if toss < 4:
             self.character.location.msg_contents("{attacker} tosses a snowball at {defender}{modifier_text} and misses wildly!", 
                                                  mapping=dict(attacker=self.character, defender=self.target, modifier_text=modifier_text))
          elif toss in [4,5]:
             self.character.location.msg_contents("{attacker} tosses a snowball at {defender}{modifier_text} and makes them duck!", 
                                                  mapping=dict(attacker=self.character, defender=self.target, modifier_text=modifier_text))
          elif toss == 6:
             self.character.location.msg_contents("{attacker} wings a snowball at {defender}{modifier_text} and strikes a glancing blow!", 
                                                  mapping=dict(attacker=self.character, defender=self.target, modifier_text=modifier_text))
          elif toss == 7:
             self.character.location.msg_contents("{attacker} wings a snowball at {defender}{modifier_text}!  Direct hit!", 
                                                  mapping=dict(attacker=self.character, defender=self.target, modifier_text=modifier_text))
          elif toss > 7:
             self.character.location.msg_contents("{attacker} wings a snowball at {defender}{modifier_text}!  Direct hit! {defender} falls over!", 
                                                  mapping=dict(attacker=self.character, defender=self.target, modifier_text=modifier_text))
 
          self.character.attributes.add('lastsnowtoss', now)
          return 
 
class SnowCoreCmdSet(CmdSet):
      def at_cmdset_creation(self):
          self.add(CmdSnow)


class SnowActiveCmdSet(CmdSet):
      def at_cmdset_creation(self):
          self.add(CmdGatherSnow) 
          self.add(CmdTossSnow)
          self.add(CmdMakeSnowAngel)
          self.add(CmdHideInSnow)
      

class Snowpile(Object):
      STYLE = '|c'

      def at_object_creation(self):
          self.cmdset.add('typeclasses.snow.SnowCoreCmdSet', permanent=True)

      def snowOn(self, **kwargs):
#          if not self.attributes.has('active') or not self.attributes.get('active'):
#             return

          session_list = [s for s in SESSIONS.get_sessions() if s.get_puppet()]
          now = time.time()

          for s in session_list:
              if not s.logged_in:
                 continue

              s_char = s.get_puppet()

              if not s_char:
                 continue      

              if not s_char.location == self.location:
                 continue

              if s.cmd_last_visible and s.cmd_last_visible + 31 * 60 > now:
                 s_char.msg(f"./~ Let it snow, let it snow, let it snow.. ./`")
#              else:
#                 logger.log_info(f"Did not show ./~ Let it snow, let it snow, let it snow.. (idle: {(now-s.cmd_last_visible)//60}m) to {s_char.key}") 
            
 
     



