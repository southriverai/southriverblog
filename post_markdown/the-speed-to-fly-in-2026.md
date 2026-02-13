# The speed to fly in 2026

When I was a kid, *The Offspring* once told me I *“would go far”*. As a paragliding pilot that answer is unsatisfactory. Questions such as “how far?” and "how do I go further?” come up nearly immediately. Now I could ask my instructors and they would tell me about the weather and reading clouds and all that stuff. If you, like me, would rather follow math than the sane and effective advice of experienced pilots. Well, here we go.

For those of you who are not paragliding pilots, some jargon. In paragliding one of the most exciting things is to cover large distances away from the point of take off. We call this cross country flying or **XC**. When flying XC we must regularly top up our altitude, or **climb**, using hotter rising columns of air we call **thermals**. If we can’t find a thermal in time we are forced to land, this is referred to as **bombing out**. A paraglider has a forward speed called **glide speed** or airspeed and a rate of falling down called **sink rate**. They can slow down by pulling their brakes or accelerate by pushing their **speedbar** (a strap or bar near the feet that tilts the glider forward). A default forward speed called **trim speed**. The speed at which the least altitude is lost per meter traveled forward is called **best glide speed**, and is usually close to **trim speed**. And the speed at which the speedbar is fully pressed is called **maximum speed**; this is described as being on ***full bar***. In general the faster you go down the faster you go forward but the trade-off between the two (**glide ratio**) is not always the same. There are 4 classes of paragliding wings, ranging from A to D which become ever faster and more dangerous.

Let us start at the beginning. Nickel and MacCready’s theorem for optimal flight speed dates back in the 1940s. Initially it was computed through an analog device or a piece of paper in the cockpit of an airplane. The basic idea of the MacCready theorem is simple. Every meter I lose flying forward I have to regain at some point in a thermal. How long that will take depends on the speed of climbing in the thermal that day. If conditions are strong and climb is fast, making up extra sink is faster than if conditions are weak and altitude is precious. 

**![][image1]**

For example: I am gliding along at a leisurely 10m/s ($V\_{gl}$) while falling (sinking) at 1m/s ($V\_{s}$). The average climb I manage to accomplish in thermals that day is also 1 m/s ($V\_{c}$) .This means for every second spent flying forward I am going to have to spend a second going up in a thermal. This halves my effective cross country speed ($V\_{xc}$). More formally:

$$  
V\_{xc} \= \\frac{V\_{gl} \\cdot V\_{c}}{V\_{c} \+ V\_{s}}  
$$

However if we want to optimize $V\_{xc}$ using $V\_{gl}$ we have to realize that sink $V\_{s}$ is actually a function of glide $V\_{gl}$ as $F\_{s}(V\_{gl})$  This is because the way we speed up is by angling our wing forwards so it will fall faster.

$$  
V\_{xc} \= \\frac{V\_{gl} \* V\_{c}}{V\_{c} \+ F\_{s}(V\_{gl})}  
$$

To maximize $V\_{xc}$ using $V\_{gl}$ we now require a derivable version of $F\_{s}(V\_{gl})$, make a derivative towards $V\_{gl}$ for the whole equation and find the 0s. 

$$  
V\_{c} \+ F\_{s}(V\_{gl}) \- V\_{gl} \* F\_s'(V\_{gl}) \= 0  
$$

Unfortunately there are many reasons why MacCready is not particularly useful for paragliding. First of all it assumes prior knowledge of where the thermals are and how strong they are going to be. Annoying, but once you have flown the first few thermals of the day you should be able to make a reasonable estimate. The bigger problem is that compared to a sailplane a paraglider has a far more limited speed range. A typical B wing can go between 20 and 55 km/h, a modern sailplane goes between 100 and 300 km/h and speeding up results in relatively smaller sink increases.

| Condition | Average Climb (m/s) | EN-B Trim (m/s) | EN-B Full Bar (m/s) | EN-D Trim (m/s) | EN-D Full Bar (m/s) |
| :---- | :---- | :---- | :---- | :---- | :---- |
| Airspeed | — | 10.56 | 13.89 | 11.11 | 16.67 |
| Still-air sink | — | 1.00 | 1.50 | 0.90 | 1.40 |
| Strong | \+4.0 | 8.44 | **10.11** | 9.08 | **12.33** |
| Moderate | \+2.0 | 7.03 | **7.94** | 7.66 | **9.81** |
| Weak | \+0.5 | **3.53** | 3.47 | 3.97 | **4.39** |

If you do the math for some modern wings with known glide ratios at various speeds, you will come to the conclusion that you should be on pretty much full bar all the time on D wings, and be on more bar than comfortable on B wings. Brakes are for thermalling, landing and ground handling. However don't remove your breaklines just yet because we have more interesting choices to make. 

MacCreadys assumes there is a known average climb that we can take advantage of at any particular moment. Perhaps the weather was different in the 1940s but this situation has not been my general experience. Instead there is a quest to find good lift. And what it means for lift to be good depends a lot on how close i am to the ground.

A more practical theory for flight dissection making is the *three zones strategy*. This idea  popularized by Niki Yotov, splits the usable atmosphere between the ground and the thermal ceiling into three zones. A progress zone, a lift zone and a survival zone. In the progress zone we ignore all but the strongest of climbs and we just try to progress for as many meters as you possibly can. In the middle zone we are looking for good lift, if we find a thermal that is above average we will use it. In the bottom zone we are afraid of bombing out, so we take whatever lift we can find. How you split the air into these zones and what you exactly do in the middle zone is a bit of a dark art and probably one of the keys to becoming better at XC flying.

Nickel and MacCready’s  formulated their theorem in a time where computers the size of buildings were mainly used to analyse German hamster wheels. Strategies like the three zones theory were first developed in the 1990s. These days every pilot carries around what amounts to a 1990s supercomputer in their pocket. We mostly use it to watch cat videos and call for retrieval but it can also simulate thousands of different flight strategies per second. *In 2026 can we choose a better speed to fly?*

## Simulating flight strategies

Essentially we are looking for some strategy that maximizes either average flight meters per flight for getting lots of nice long flights. Or a riskier strategy that maximizes flight distance in the top 10% of flights, for those braggable distance records. We choose this strategy by comparing it to others in a simulation engine.

We can simplify this simulation a lot. We have established that when you are not thermalling you should be pretty much on full bar all the time unless you are flying in the weakest of conditions. So the question posed to our strategy can be brought back to a 2 option problem: If I am in a thermal, given my flight track so far, do I **A: thermal** or **B: progress at full bar**? Our previous conclusion on optimals speeds also means the models of the wing can be reduced to two numbers as well: max speed and sink at max speed. 

As a reference we can define some simple strategy:

* **Never therma**l: never thermal but always progress at max speed, this is sometimes described as an accelerated sled ride  
* **Always thermal**: always thermal as much as you can and then progress at max speed to the next thermal.

We can compare this to a more refined strategy:

* **Three zones**: we split the usable altitude space into three equal zones, in the bottom zone we use all thermals, in the middle zone we use thermals if they were stronger than the median of all previous thermals, and in the progress zone we only thermal if they are stronger than 90% of all thermals seen that day.

Flights in my simulations take a maximum of six hours. I chose to simulate in relatively weak conditions, on average 0.5 m/s effective climb. Once the effective climbs come close to 2 m/s going up becomes so easy that taking smart decisions on lift quickly becomes irrelevant and all strategies perform similarly. Thermal spacing seems the hardest parameter to model. In real life often the pilot has some inclination how much further the next one is depending on terrain. There is also a relation between the strength of atmospheric conditions and how many thermals show up. In the end I decided to have the distance between them follow a normal distribution with a mean 2 km with a standard deviation 1 km.

**![][image2]**

Now let's be honest, this is a very shit atmospheric model. There are some obvious improvements that can be made to it but in all honesty building just a good model for thermal distributions with their changing strength, slowdown and speedups is its own topic for another time. I have heard wind might be important to paragliding as well. So I would ask you to bear with me in a limited suspension of disbelief and just enjoy some numerics.

Using our simulator we can compare different versions of the three zones strategy. Using a simple loop we can optimize the percentile threshold for the progress and lift zone that we want.  
However we can take this one step further beyond. Instead of having a parametric model we can do some deep learning magic. The neural network strategy uses a model that takes the flight track up until now as input and produces a decision to use a thermal or not. I used a relatively small neural network that I trained with some simple reinforcement learning. A comparison of the various strategies is shown below.

| Strategy Name | Median distance flown (km) | Top 10% of distance flown (km) |
| ----- | ----- | ----- |
| NeverThermal | 10.02 | 10.03 |
| AlwaysThermal | 63.74 | 69.82 |
| ThreeZones (1.0, 0.7) | 71.94 | 82.56 |
| ThreeZones (0.9, 0.5) | 74.76 | **84.26** |
| ThreeZones (0.8, 0.3) | **76.05** | 83.85 |
| ThreeZones (0.7, 0.1) | 74.57 | 81.69 |
| **NeuralNetwork** | **81.20** | **87.19** |

After running some experiments three things become apparent. First of all, **always thermalling** is not terrible, honestly this is the strategy that I generally follow. Note there is an implicit lower threshold here as we don't simulate thermals smaller than 0.2 m/s. Second of all, though the **Three Zones** median distance is not that much better in median distance covered, the longest flights are much longer. It is sort of intuitive that on a good day, not being critical about lift is holding you back more than on an average day. Finally the **Neural Network** strategy does similarly to the **Three Zones** on record flights, it is far more reliable. The median flown distance is nearly 10% higher due to far less bombing out. Is the **Neural Network** strategy the speed to fly in 2026 then? I have not quite convinced myself. To me there seem to be at least three key elements missing in this strategy.  
![][image3] 

Wind matters, but local wind is easily accounted for. We convert airspeed to effective groupspeed and rerun our optimal speed calculations. When going against the wind the case for flying at max speed rather than trim speed only enhances. In fact any sort of instrument will indicate that this would increase the effective glide ratio. When flying with the wind the choice of speed comes back into the picture though. Especially in weaker conditions and on slower wings a little bit of tailwind might make our speed decision more complicated than flying maximum speed all the time.

The most complicated factor that makes me doubt these strategies are terrain and clouds. Not only do I need altitude to clear ridges along my paths. Terrain and clouds also inform my expectation of finding lift. In many flight situations going into or above the clouds is not really an option but they do inform which paths are safe to take and where lift can be reasonably found.

A final limitation is that atmospherics, a thermal, is not just a 200m wide uniform column of lifting air. The strength of a thermal varies in both distance from the centre and altitude in ways that are non trivial. They are generally weaker close to the ground and stronger around mid day. There are also types of lift like ridgelift and convergences that are even more important when flying longer distances. Some of this can be managed by feeling and skill. Yet more advanced instruments will track these dimensions of thermals for you and help you make more informed decisions. 

*Do you think you can do better?*   
*All the code used for this experiment is published at:*  
[*https://github.com/southriverai/paraai/tree/fa028e4329613f1a3e47e2f78751b3979c086744*](https://github.com/southriverai/paraai/tree/fa028e4329613f1a3e47e2f78751b3979c086744)  
*Write your own strategies and compete\!*

## What is next?

A few weeks ago a little bird landed on my window still and deposited in my S3 bucket over a million hours of paragliding flight time from across the globe. In this data pilots flew an estimated 2 million thermals and some of them several times in a single day. I think this is enough data to create an accurate model of, in the very least, conventional thermal lift and use that to make more realistic simulations. Stay tuned for more flying machine learning\!

[image1]: images/1sdVTjVopYT-bKBhNCjK0Qc8PYZhKL7pa-qbuI6LG-R4/image3.png

[image2]: images/1sdVTjVopYT-bKBhNCjK0Qc8PYZhKL7pa-qbuI6LG-R4/image1.png

[image3]: images/1sdVTjVopYT-bKBhNCjK0Qc8PYZhKL7pa-qbuI6LG-R4/image2.png