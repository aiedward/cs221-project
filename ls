[33mcommit 07b31cbef6cb47844102d7e4c55cd7e27d01de17[m
Author: Austin <aray@cs.stanford.edu>
Date:   Tue Dec 8 23:46:10 2015 -0800

    See last commit message.

[33mcommit 263686d726351e75f8efbe2662c3983a3a369557[m
Author: Austin <aray@cs.stanford.edu>
Date:   Tue Dec 8 23:45:54 2015 -0800

    Alright, you can now run anything from the cs221-project folder. Run 'python -m recipe-writer <some executable> <args to that exectuable>' where <some executable> is process_recipes, query_online_db, or write_recipes (for now) and <args to that executable> would be normal space-separated arguments you'd pass to your executable if you were running it normally from the command prompt.

[33mcommit fedbf83029011a6bf5301199cc256045e15ee7f9[m
Merge: 46a2a64 2da939d
Author: Alex Lin <alin719@stanford.edu>
Date:   Tue Dec 8 23:11:42 2015 -0800

    Merge branch 'master' of https://github.com/austospumanto/cs221-project

[33mcommit 46a2a6464d5cca1e547b26503f786167e5029a94[m
Author: Alex Lin <alin719@stanford.edu>
Date:   Tue Dec 8 23:11:33 2015 -0800

    did some test databases, adding more api keys

[33mcommit 2da939d9f3bb1c5ae294069f99f20daa0518feb0[m
Author: Austin <aray@cs.stanford.edu>
Date:   Tue Dec 8 22:32:29 2015 -0800

    Reorganized the repo. Buggy still, but this will be for the better. I'll provide a full README.txt when I'm done.

[33mcommit c0ac2eb211952bfa8a77bacb2cb0ffdc3701f29e[m
Author: Austin <aray@cs.stanford.edu>
Date:   Tue Dec 8 20:20:06 2015 -0800

    Running processJsonRecipes.py now outputs a file starting with 'aliasData' that contains information about ingredients in json form.

[33mcommit 9c5bbdcb904201743d7b626cd37b81bbd6c8567e[m
Author: Austin <aray@cs.stanford.edu>
Date:   Tue Dec 8 17:32:06 2015 -0800

    Making more progress with processJsonRecipes.py.

[33mcommit f36de69d1198f71820acfc02fe2c345992c5ce99[m
Author: Austin <aray@cs.stanford.edu>
Date:   Tue Dec 8 16:42:26 2015 -0800

    Working on processJsonRecipes.py, which will preprocess json recipes so our actual executable runs faster.

[33mcommit 178a5b65e8ddb201b6a6421ffc0710640e51696d[m
Author: Austin <aray@cs.stanford.edu>
Date:   Tue Dec 8 15:56:40 2015 -0800

    Organized our repo into binary files, library files, resource files, and backup files.

[33mcommit f29b9f7eddeac220cb924e9c37192a9d1de1b386[m
Author: Alex Lin <alin719@stanford.edu>
Date:   Sun Dec 6 14:53:55 2015 -0800

    pulling everything to dl from databases on other comps

[33mcommit 03f2d29ed69830226ba2aac982a42defe1bc6a21[m
Merge: b213b1a d7e2403
Author: martinob <bdmartino@gmail.com>
Date:   Fri Dec 4 12:10:57 2015 -0800

    Merge branch 'database'

[33mcommit d7e24032b27089dd7d32fc90300521f8cfd6119c[m
Author: martinob <bdmartino@gmail.com>
Date:   Fri Dec 4 12:10:12 2015 -0800

    Database should fucking work now!!

[33mcommit b213b1a9745bd3a2c5afaed2e0d3df6a77ffc8fc[m
Author: Austin <aray@cs.stanford.edu>
Date:   Sun Nov 29 04:00:18 2015 -0800

    Did a temporary fix for the infinite loop problem.

[33mcommit 26deb6080ffe47d6793a2a9a794bb9d76f2b3b2d[m
Author: Austin <aray@cs.stanford.edu>
Date:   Sun Nov 29 03:53:41 2015 -0800

    Dear lord. It works. The C++ version is officially ported to the Python version.

[33mcommit 9ac17407a7888f5e4b41030916f8f2f106efffb9[m
Author: Austin <aray@cs.stanford.edu>
Date:   Fri Nov 27 23:27:10 2015 -0800

    Bigram dictionaries and ingredient end-word-bigram dictionaries are both properly formed now. Writing ingredients/instructions still buggy.

[33mcommit 0ef81d1e864336e5842b66ca142b2eed3ac99ac5[m
Author: Austin <aray@cs.stanford.edu>
Date:   Fri Nov 27 19:46:00 2015 -0800

    Making good progress on cleaning up recipewriter code.

[33mcommit 4c70b6eb7d565e5597c0d402f52758e18ed7aa13[m
Author: Austin <aray@cs.stanford.edu>
Date:   Fri Nov 27 13:54:34 2015 -0800

    Figured out python's pass-by-object-reference system in sandbox.py. Check it out.

[33mcommit d6be9f2d5a95d33e70899c804ce3a671f3f47513[m
Author: Austin <aray@cs.stanford.edu>
Date:   Fri Nov 27 13:26:54 2015 -0800

    Still cleaning/commenting recipewriter.py.

[33mcommit 6f1a9943cca4ccd0bab7f37a53fce397854b09a5[m
Author: martinob <bdmartino@gmail.com>
Date:   Wed Nov 25 15:22:12 2015 -0800

    database.py should get as many recipes as we want now, will do some more testing just in case

[33mcommit 5f6bca870920cf03561f1b7bd055b7e1bb50a99a[m
Author: martinob <bdmartino@gmail.com>
Date:   Wed Nov 25 15:21:15 2015 -0800

    Made improvements in the database.py so that it doesn't crash when the json files fromt he APIs we call are broken (i.e. missing attribute).

[33mcommit c9bc8f8a0fe13ad146745e3a74fa39602766b577[m
Merge: 4491fc9 2b308f8
Author: martinob <bdmartino@gmail.com>
Date:   Tue Nov 24 18:23:29 2015 -0800

    Merge branch 'master' of https://github.com/austospumanto/cs221-project

[33mcommit 4491fc929a4bcd97a10dc997d12d143351abb56b[m
Author: martinob <bdmartino@gmail.com>
Date:   Tue Nov 24 18:22:24 2015 -0800

    Big improvements in database.py. No more broke requests due to government API timeout due to check and sleep. Moreover, we now store more attributes per recipe, such as time to cook, flavors, and cuisine. Added comments to help read the code

[33mcommit 2b308f878e2e05ca57a3fc887fe46c7720df1edb[m
Author: Austin <aray@cs.stanford.edu>
Date:   Tue Nov 24 14:53:51 2015 -0800

    In the process of cleaning up recipewriter.py. Cleaning will help me understand the original algorithm as well.

[33mcommit fce6550253d3601de0031f0306f8d62899b6b737[m
Author: martinob <bdmartino@gmail.com>
Date:   Tue Nov 24 14:01:46 2015 -0800

    Small changes to start coding again

[33mcommit 9aeb38891745aea2bfd5df4b36318b6530958d31[m
Author: martinob <bdmartino@gmail.com>
Date:   Thu Nov 12 21:29:10 2015 -0800

    trying to fucking merge

[33mcommit 2cccf8def84ebb8066c21af65360dd72256796fe[m
Merge: 51b7c87 f8a4f08
Author: martinob <bdmartino@gmail.com>
Date:   Thu Nov 12 21:26:37 2015 -0800

    Merge branch 'master' of https://github.com/austospumanto/cs221-project

[33mcommit 51b7c87421bdb41e08b939f3a830ee54b4d29976[m
Author: martinob <bdmartino@gmail.com>
Date:   Thu Nov 12 21:19:51 2015 -0800

    Made progress on database, now getting recipes from yummly and getting the nutritional calue of the ingredients in those recipes. Both the Recipe and the Nutriotional database work, and I write them on an external problem. Next time is to figure out a way around the 1000 API call per hour limit from the government API

[33mcommit f8a4f086a8603ca24103ab39e5901f9e243908c2[m
Author: Austin <aray@cs.stanford.edu>
Date:   Thu Nov 12 20:56:21 2015 -0800

    Clean build. Have not had a clean run yet. Need to debug.

[33mcommit 92c433537ba58230f593f5b8e7c6d90d41200292[m
Author: Austin <aray@cs.stanford.edu>
Date:   Thu Nov 12 19:23:59 2015 -0800

    No more build errors! Now to get rid of runtime errors...

[33mcommit ba04b9f36bcef9d6f41844ce10cb8c17a3118835[m
Author: Austin <aray@cs.stanford.edu>
Date:   Thu Nov 12 04:39:15 2015 -0800

    Revert "Made improvements to now also connect with the government API. Still struggling to get ALL data from both APIs with one call, might need to break it down into several small calls instead."
    
    This reverts commit 49d1c4cb9b9ba9c1f7dc21f77c8ed9a6f553d00c.

[33mcommit 7aa9f152fbd24a084032cb11de8d50e34887f34c[m
Merge: 49d1c4c 22d8eb6
Author: Austin <aray@cs.stanford.edu>
Date:   Thu Nov 12 04:32:27 2015 -0800

    Merge branch 'porting-c++-code'

[33mcommit 22d8eb68da817f388a08f42d8e298577f5c35a3e[m
Author: Austin <aray@cs.stanford.edu>
Date:   Thu Nov 12 04:32:03 2015 -0800

    Converted vast majority of RecipeWriter code to Python from C++. Still have to convert the i/o code (for reading cookbook from file) but that's all.

[33mcommit 49d1c4cb9b9ba9c1f7dc21f77c8ed9a6f553d00c[m
Author: martinob <bdmartino@gmail.com>
Date:   Thu Nov 12 02:43:46 2015 -0800

    Made improvements to now also connect with the government API. Still struggling to get ALL data from both APIs with one call, might need to break it down into several small calls instead.

[33mcommit dd387dd627d161e0f4a49d