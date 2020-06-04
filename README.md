# pypadlet-glitch

Discord Bot that sends regular updates of any posts made to specified public Padlet.  
Uses <span>discord.</span>py and Padlet's REST API, and hosted on Glitch.  
  
## I really want Padlet bot on my server!
To invite the bot to your Discord server, any server admin may click [this link](https://discord.com/api/oauth2/authorize?client_id=699187439532507216&permissions=537390160&scope=bot).
  
## Glitch Files 
There are a bunch of files that Glitch requires in order to run the bot, and it's made a little more complicated because the bot is written in Python (I'm sorry). Briefly,  
* **<span>start.</span>sh** is just command line stuff that Glitch runs. Here's where Python is installed with the virtual environment provided. 
* **requirements.txt** is the file that has all the additional libraries that need to be installed, and <span>start.</span>sh checks here to figure out what else to install.
* **watch.json** tells Glitch what to do when changes are made to the files - if it is listed under `install`, Glitch re-runs the install process, and if it is listed under `restart`, just the bot files are re-run. The `throttle` field here specifies the intervals between Glitch's check for changes (otherwise it checks like every second and restarts 4 times when you type one line of code).
  
_Only found in Glitch directory:_
* **.env** contains the secret Discord Developer Token (plz no stel!!) and the Padlet App ID for the bot. It isn't on Github because security, but also Discord polices for exposed tokens, and if they catch it out in the open (i.e. in a public repo), they'll cancel that existing token and regenerate one - and bot will die due to authentication failure :(
  
## Customizing the bot
Under **config_main.json**, there are a bunch of fields that can be changed to tweak the bot's behaviour.
* `Padlet -> Name & URL`: To link to the target Padlet. (Psst, the name is just a formality, the URL is where it's at!!!)
* `Discord -> Channels -> allowed`: An array of names of the allowed channels (Again, a formality, just for bug fixing and readability).
* `Discord -> Channels -> posting-channel`: The channel ID of where the update embeds should be sent. To find this, open up Discord and right click the desired channel in the server and click "Copy ID". 
* `Discord -> Bot Mention`: The prefix to use in Discord to run bot commands.
* `Discord -> Time between loop`: The interval _in minutes_ between checks on the Padlet to see if any new posts have been made.
  
For easy testing and debugging, **config_test.json** has been kept here - just change the reference in **<span>bot.</span>py** to the right target json file.  

## Syncing with Glitch
Unfortunately there is no way to do this automagically :( Head over to the [Glitch project](https://glitch.com/edit/#!/knav-pypadlet-glitch) and import from this GitHub repository. 
