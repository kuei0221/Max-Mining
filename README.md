Greeting.

This is a record for a my work of a trading mining project during Dec in 2018.
Now the project is no longer profitable, so I put my code up here as a record.
This robot is not fully completed yet, since the opportunity no longer exist faster than I expected, and I might not update it I find another similar opportunity. But during the time I still runing it, it can successfully make thousands of trade per days for nearly a month, and eventually made a 70% return.

Here is how it works:
  account.ini should have your two accounts' api key and secret, also the two type of currency you are going to use
  api.py provides the function to build the connection to exchange with Restful api
  launch.py include a simple function to get your account's data
  trade.py is the main script which which will run the trade
  main.py is the monitor to control the order flow. Run this to start the robot.


This project works based on Max exchange, so it will face problem if it run on other exchange.
The profit can be split into two part - 1,Trading Reward and 2,Airdrop reward.

1.Trading Reward.
For any trade you made, the exchange will return certain degree of the fee you paid back to us through equivalent value of MAX coin. The amount of degree will decline as the difficulty of Mining increase, initially it was 60%.
The fee we paid, will automatically be selled at market to buy Max coin with at the same time when the order is completed.

2.Airdrop Reward
At the end of the day, the exchange will return 80% of its net fee profit back to the user by Max coin. For each users, it will return 40% of the total fee that trade made to maker and 10% to taker. The remain part will then go to holders, but it was then be decide by time-weight factor requiring you lock the money which is not suitable for our strategy, so I will not consider that in this project.
In short, if you can become maker and taker at the same time, you can take 50% of total fee per trade back.


So here is the strategy:

We become maker and taker at the same time, so for any trade we made, we will get 60% of the fee back in Max now and 50% back at end of the day.
That will be 10% return for the fee we paid.
Since the profit is based on "fee", we need to make thousand of trade to get an ideal profit. And while the trade goes on, the total amount of money will decline since only part of the fee were refund immediately. I have made an Excel chart to simulate the change of total fund, and found out the marginal is diminishing. Therefore, I have chosen 1000~2000 as the number of the trade to do per day which provides relatively large profit but not too much trade to do. 

Another important things to consider is that MAX coin from trading reward will be bought at market order automatically after our trade done, so if the market do not have enough depth (it is), it will push up the Max price and increase our cost of MAX.
We can maker a limit sell order of Max right after the reward arrive to solve this to provide some protection. When the system going to buy at market, our order will then be executed and provide some depth to avoid the price pushing. To do this you have to remain some MAX at the end of the day.
That is , we are taking the order buy ourselves (system buy at market <-> sell at limit, and the amount system bought will return to us).

Besids, since we have to sell the all the max at the end of the day, Max coin will face a dramatic pressue of selling, and we will be lose some part of revenue if the price falling down. Luckily, it seems that there is an official protection of the price, Max coin generally holds at 0.081( to usdt). This is the prerequisite of our strategy, once it no longer holds please stop the system immediately.

by Michael, 2018/12/21

(2019/04/10 updated)
