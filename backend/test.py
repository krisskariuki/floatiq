from scraper import Navigator
from scraper import Action

mozzartNavigator=Navigator('https://www.mozzartbet.co.ke/en#/casino')

mozzartActions=[
Action(action='click',attribute='class="login-link mozzart_ke"'),
Action(action='write',attribute='placeholder="Mobile number"',inputValue='0113294793'),
Action(action='send',attribute='placeholder="Password"',inputValue='Chri570ph3r.',delay=0),
Action(action='click',attribute='alt="Aviator"'),
Action(action='loop',delay=10)
]
mozzartNavigator.navigate(mozzartActions)