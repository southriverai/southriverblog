# A slightly more advanced model for paragliding atmospherics

“Is it working?”  
A strange innocuous question you will hear on paragliding takeoffs around the world. The question does not pertain to some machine or instrument, but to the state of the atmosphere. The pilot in question is wondering if the lifting air in the area has strengthened to the level where a pilot can stay up indefinitely. Implicitly they divide the myriad of conditions and variations the air above them can have into two categories: paraglidable or not-paraglidable.

[Previously I built a paragliding strategy using reinforcement learning](https://southriverai.github.io/southriverblog/post.html?slug=the-speed-to-fly-in-2026). To grant this approach a skein of practical applicability it will need a much much better model of thermal lift. I will need to break up the word paraglidable into various distributions that I can then plug into my simulator and torture my assortment of computers for another few days.

## Some basics

An experienced pilot once compared a column of rising air to an elevator. Even if it is a very big powerful elevator it can lift 12, perhaps 20 people. In a serious competition over a hundred pilots can be climbing in the same column without it slowing down or running out. Imagine that awesome power. Lifting thousands of kilograms up into the ski at a brisk running pace without slowing down. And there is not one of those columns out there, often there are dozens if not hundreds in a single valley. 

The example above begs the question how much usable power there is in the atmosphere on a typical day. Let's start with the input. At the orbit of planet earth the sun provided 1360 Watt per square meter pointed directly at the sun. The earth is not flat, but closer to a sphere. Due to foreshortening the actual wattage that falls upon a square meter of the outer atmosphere at the poles is much lower than at the equator. The earth is a sphere but the projection of the earth on the sun is a one-sided circle. The difference is a factor of 4, therefore on average, poles to equator, day and not only about 340 Watt per square meter falls on the earth's outer atmosphere..

Now this is where things get very complicated very quickly. The outer atmosphere absorbs and reflects some of that light, clouds reflect even more. The angle at which the sun faces the surface even averaged over many square kilometers to compensate for geography depends on season, latitude, and time of day; it therefore serves to be specific. 

In the area where I fly often, around Plovdiv, located in central Bulgaria at 41 degrees latitude,  the summer sun heats the ground with [about 200 W of solar](https://courses.ems.psu.edu/meteo469/book/export/html/202) over a 24h cycle. Most of that heat is radiated back into space and only 30W is converted into rising air. Most of this, but not all, happens during the day so as a ballpark figure we can take 60W per square meters. In a previous article I calculated that a paraglider needs about 1300 Watt to stay up. So every wing only needs about 22 square meters dedicated to them to keep them flying. Strangely this is about the surface area of a typical wing.

We can also approach the energy question from the other direction. How much power does a good thermal use?  Let's imagine nice well developed thermal on a good day. It has a radius of about 100m and goes up at 3m/s, given that a paraglider sinks is over 1m/s this would show up as a 2m/s climb. Lets say this one takes us up 500m. How much power does this actually use? The volume of the moving air can be computed as:

$$  
\\pi \\cdot 100\\,\\mathrm{m}^2 \\cdot 500\\,\\mathrm{m}  
\= 1.57 \\times 10^{7}\\,\\mathrm{m}^3  
$$ 

Air weighs about 1.1 kg per cubic meter.    
Moving that up 3 meters every second. Since potential height energy is mass height  Gravity the amount of energy added to the air in 

$$  
3\\,\\mathrm{m/s} \\cdot 1.1\\,\\mathrm{kg/m^3} \\cdot 1.57 \\times 10^{7}\\,\\mathrm{m^3} \\cdot g  
\= 5.181 \\times 10^{7}\\,\\mathrm{W}  
$$

50 MW is about the power of a french nuclear submarine. Note that there is a bit of hand waving here since just a few hundred meters away there will also be a cold column of air of equal mass going down but let us ignore that for the sake of having big simple numbers.

$$  
\\frac{50 \\times 10^{6}\\,\\mathrm{W}}{60\\,\\mathrm{W/m^2}}  
\\approx 8.33 \\times 10^{5}\\,\\mathrm{m^2}  
\\approx 0.83\\,\\mathrm{km^2}  
$$

Even if we build in the width of thermals this means at the height of our Bulgarian summer day I would have to travel at about 800m to get from one thermal to the next.

## Building an atmospheric model.

To analyse thermal lift it will use paragliding track logs from various sources. Let's take a moment to reflect on the huge bias that is implicit in the way this data snuck onto my hard drive. It supposes somewhere a pilot woke up in the morning, looked at the sky, decided to try and go fly. In that place. On that day. They made their way to a take off site and found a thermal waiting for them. They then flew around for some time and afterwards found the flight worthy of uploading it to some public server that was kind enough to not limit me in downloading it in bulk. While people are flying more and more, all over the world, all the time, it has to be said that almost 90% of logged flights were flown in Europe, and over 80% of logged European flights occurred in the alps. I can't hope to quantify the biases this sequence of events introduced into my data, but suffice to say I am building a model of lift as typically encountered by typical European alpine paragliders and not a general model of atmospherics. 

Besides this it is also important to note that not everyone climbs at the same rate in the same thermal, some people are better at finding the fastest rising air in the core of a thermal, they might also keep their wing flatter while turning and limit variations in pitch. This and other factors might give them a better effective climb in the same column of air; what the actual distribution of air velocities in that column is, is another question entirely. I will average over all of these and only deal with average effective climb over all pilots.

To improve my reinforcement learning model for paragliding strategy in need of specific answers to specific questions I will go over them one by one and how I attempted to answer them. But before I do I want to spend a moment looking at how I analyse a tracklog. Below is a rendering of the tracklog of one of my incredible oktober flights in India.

![][image1]

First of all I remove noise with a kahlman filter. Tracklogs often contain sudden 100m/s climbs and descents that are clearly resulting from measurement noise/gps spoofing/ accidentally touching a vario in a sensitive place. Then I resample to a constant 1 second timescale and apply a gaussian filter with a stand deviation of 60 second to filter the altitude component which even after removing the offending timepoints is still the most noisy. Finally I split the track into three types flying: 

* Progression: Long straight lines that cover distance at max. At some point I might use these to estimate global wind and such but for now they only serve to estimate distance between thermals.   
* Climb: Spinning little spirals that have constant significant climb for at least a minute.  
* Exploration: Basically everything that does not fit the other two categories, whether it is unsuccessful scratching (flying close to terrain in search for marginal lift), finding where a thermal starts, or just making a circle to shoot a photo of a friend.


In this way I analysed well over a 2 million flights with 19 million climbs in order to improve my atmospheric model.

### 

### My previous model

My previous model has 3 different random variables to populate:   
$X\_c$ Altitude of the ceiling in meters  
$X\_d$ Distance between thermals in meters:  
$V\_c$ Strength of climb

Here is the model I used in my previous article  
$$  
X\_c \= 1000  
X\_d \\sim \\mathcal{N}(2000, 1000)\\;\\big|\\;\[200,3000\]  
V\_c \\sim \\mathcal{N}(0.5, 0.5)\\;\\big|\\;\[0.1,8\]  
$$

Besides getting more realistic estimates for many of these values I also want to incorporate time of year and time of day into climb strengths to create a more natural end to flights. Climbs within a thermal are also not uniform in speed. Leaving them early and entering them above their start can be strategic.

Here is the model I used in my previous article

$T\_y$ Time of year in days:   
$T\_d$ Time of day in hours:   
$X\_a$ Altitude at the moment of climbing.

$$  
X\_d \\sim \\mathcal{X\_2}  
X\_c \\sim \\mathcal{X\_2}(2000, 1000)\\;\\big|\\;\[200,3000\]  
V\_c \\sim \\mathcal{X\_2}(0.5, 0.5)\\;\\big|\\;\[0.1,8\]  
F\_y \=   
F\_d \=  
F\_x \=   
$$

Have climb speeds been going up over the years? 

Over the last few decades wings have been getting better, perhaps pilots too. My data stretches from 1995 to 2025\.  Both stories of more experienced pilots and according to sites like compareglider.com glide ratios and other wing statistics have been improving over this period. If climb speeds have been going up this could distort the data.

![][image2]

From 2000 to 2024 mean climbs have been more or less constant though. Before 2000 there is not that much data to go on and the strange drop in 2025 warrants some deeper exploration. For now I will just exclude that data and assume climbs across the other 25 years are roughly comparable. So if you are reading this while climbing at a speed over 1/ms, congratulations you are doing better than average. Now stop looking at your phone\!

### How does climb speed differ throughout the year?

![][image3]  
I knew climbs are stronger in summer but I always figured the difference would be bigger. Far fewer people fly in winter and many of those who do fly with skis and mittens fly straight to landing. I am only looking at climbs right now and perhaps a more comprehensive flight analysis is in order to get a more realistic picture. Another interesting note is how the speed of climbs actually goes down a bit during the summer months.

### What is the distribution of distance travelled between thermals given the mean climb of a flight?

This is a bit of a trash question. The vast majority of flights in which thermals are encountered are flown in mountainous terrain where the geometry informs pilots where lift should be searched. In fact it is not only a question of distance, often you also need sufficient height to access a ridge where you have an expectation of finding more and better lift. However since my previous model had this as a parameter I would like to get a real world estimate of this.  
![][image4]  
My expectation had been that lower mean climb means fewer usable thermals and longer distances between climbs. In summer months climbs are stronger hence shorter progress segments. This relationship did not materialize. In fact the opposite seems to be true. Stronger lift means people are probably more confident in taking larger jumps. In the end very little conclusions can be drawn from this relationship and what I am left with is a better estimate of the distribution (which I shall call Chi-square-ish) of distance between thermals.

How does thermal strength vary within a single thermal?

Conventional wisdom states that thermals form when little bubbles of hot wet air happen to find each other in a certain point in the terrain referred to as the trigger point. Together they start rising, finding more friends along the way and accelerating their climb. Eventually they either cool enough to start condensation and form a cloud, or hit a layer of air that is no longer heavier than they are and the thermal then slows down and stops. 

Strategically as a pilot you want to be using the strongest section of the climb every time you top up your height but at what altitude that section can be found, is not always clear. In the flight shown above, climbs kept getting faster the higher up I went, until I had neither the balls nor the mittens to go higher. There was also an *inversion* around 3000 meters where, due to a layer of warmer, air it was harder to climb. Although this happens regularly I am going to ignore these in my models on this pass.

![][image5]

There are at least two ways to look at the variation of climb speed within a thermal. On the one hand every thermal has its own dynamic. Close to the bottom it is not fully formed, the rising air might be spread over a larger area and might not have gathered much momentum. Near the top the energy might have run out, the thermal has run into a warmer layer or stronger wind might disperse the energy. All of these dynamics also play out over the whole of the usable atmosphere as well as within every thermal. I therefore analyzed climbs individually and on a per flight basis. I then normalized the altitude to a 0 to 1 domain and rescaled the velocity in relation to the mean and aggregated the outcomes.

The results are relatively similar if you look at climb strength. The strongest climbs can be found in the centre section of a thermal and in the centre section of the usable atmosphere. In theory we could construct a climb efficiency metric from this. Avoid the bottom section and do not linger too long and a pilot can climb almost twice as fast as if he had ridden the thermal from bottom to top. If we know the place and strength of all thermals in a flight and meter spend climbing in one thermal could have been traded for a meter climbing faster in another. How far from optimal has a pilot made their choices?

If we look at time-spent-at-altitude the picture is a bit different. While within a single climb pilots spend most of their time starting at the bottom and lingering too long at the top, over the whole atmosphere time is spent more uniformly. Some of that is the central limit theorem acting over the sum of several times the per-climb distribution. Yet some of it is certainly the pilot avoiding the ground and failing to achieve their maximum height as well.

### How high can I climb and how much does that depend on climb speed?

The highest a pilot can climb depends first and foremost on where he is flying. Thermals form on peaks and ridges and often they run out of power long before they hit the clouds. In the alps it is pretty rare to find a thermal that will take you above 4000m, in the himalayas that is every friday afternoon. 

![][image6]  
Weather conditions also matter. To quantify how much I looked at the relation between the highest point in a flight, what time of year that flight was flown and how fast the climbs in that flight were. Upon inspection the relation between time of year and highest achieved altitude seems rather weak. Of course flights generally go higher in summer but that increase can be almost completely explained by the increase in climb strength in summer.

The relation between climb strength and the highest point achieved in a flight is stronger but less straight forward. Climbs above 1.5 m/s are often found in a context where the climbs are capped by a warmer layer of air limiting further progress. This layer is often exceedingly difficult to penetrate and above it lift is perhaps even harder to find. Therefore the maximum height reached in flights with the strongest climbs is often much lower.

### When does a flying day start and end?

There is a magic moment at the end of every flight. You have run out of options, out of lift, you have fallen below the altitude where you find reasonable lift and you need to come in for landing. Sometimes you get an encode when cold air from a nearby mountain slides underneath the last warmth on the ground and gives you just that little bit more. A last question for my model is when pilots are forced to land at various times of the year.   
![][image7]  
The plot above has split all climbs in a per month bins and fits their strength and distribution with a sine in the first case and a gaussian in the second. Out of all our previous exercises, survivors bias is the biggest influence here. I can only judge the strength of thermals at dinner time in summer for people that have managed to stay up that long and have again found a climb rather than sitting down at a local fish restaurant. To compensate for this I gathered their distribution as well. If only 2% of all climbs occur after 18:00 (germanic dinner time) we can infer that these might be the strongest 2% of all climbs that can still be found. If that makes some of the more data savvy readers cringe, consider the alternative, modeling not only the climb itself but also the behavior of the pilot that generated it.

## Next steps

I am leaving a bunch of other questions on the cutting floor here. Most of these relate to thermal geometry, width, location, thermal tilt. I suspect I will circle back to these in a future installment. But if you would like to beat me to it all the code is public at   
\#paraai

In the end all of this is an exercise to make my simulator suck slightly less and make the decision derived from the resulting machine learning policy have slightly more relevance to reality. The next step is to incorporate these distributions into my machine learning model and upgrade both the sim and the learning models.

## 

## Acknowledgement

As this project is now growing there are some people I need to thank for their contributions. I would like to thank Michael von Känel from KK7 for providing me with most of the data and making my life easier by preprocessing it. Nikolay Yotov for providing feedback on this article and Philippe Larcher for making me slightly less of a flying idiot on a continuing basis.  


[image1]: images/1OfDB28B9jqOYbgebBZWsacBjSGKuWecVGCqM1T8iU8A/image1.png

[image2]: images/1OfDB28B9jqOYbgebBZWsacBjSGKuWecVGCqM1T8iU8A/image3.png

[image3]: images/1OfDB28B9jqOYbgebBZWsacBjSGKuWecVGCqM1T8iU8A/image5.png

[image4]: images/1OfDB28B9jqOYbgebBZWsacBjSGKuWecVGCqM1T8iU8A/image4.png

[image5]: images/1OfDB28B9jqOYbgebBZWsacBjSGKuWecVGCqM1T8iU8A/image7.png

[image6]: images/1OfDB28B9jqOYbgebBZWsacBjSGKuWecVGCqM1T8iU8A/image6.png

[image7]: images/1OfDB28B9jqOYbgebBZWsacBjSGKuWecVGCqM1T8iU8A/image2.png