a = {
     'title' : "Amal and Armaan Malik: A making of their own name in the Music Industry",
     'PostedOn' : 'January 07, 2016',
     'Desc' : """ Bollywood seems to be reading its finest chapter. It has not only begun to produce worldwide blockbusters and theater delights but also can stand lofty and boast of the young talents that join it.""",
     'link' : 'Amal-and-Armaan-Malik',
     'blogid' : 25,
     'blogHTML': """ 
     <p>Bollywood seems to be reading its finest chapter. It has not only begun to produce worldwide blockbusters and theater delights but also can stand lofty and boast of the young talents that join it.The latest additions to the list are two fresh entrants in music industry: Amal and Armaan Malik. The brother duo has made its presence felt with the most trending songs like &lsquo;Main Hoon Hero Tera&rsquo;,&lsquo;Soch Na Sake&rsquo;, &lsquo;Main Rahoon Ya Naa Rahoon&rsquo;, &lsquo;Zindagi Aa Raha Hoon Mai&rsquo;, &lsquo;Love You Till TheEnd&rsquo; and &lsquo;Auliya&rsquo; to name a few.</p><figure data-orig-width="400" data-orig-height="261" class="tmblr-full"><img src="http://40.media.tumblr.com/29fff412e36e32beb7ac11a9de816134/tumblr_inline_o0jslavOB31ta6vks_400.png" alt="image" data-orig-width="400" data-orig-height="261" width="400" height="261"></figure><p><br></p><p>Still in their early 20&rsquo;s, composer Amal and singer Armaan are a trending topic amongst the buzzlovers only because of their talent and toil. Sons of singer and music director Daboo Malik, and nephew of renowned music director Anu Malik, these folks are like breathe of fresh air in the music industry<br></p><p>.&ldquo;They are one of the most enthusiastic young singers I know. To make melody comes from their father but the energy is all them. They strike the right chords, the right feel.&rdquo; these words of Salman Khan appositely define their talent.</p><p>All the melodies that they produce are adored by music aficionados. Amaal is one of the few &nbsp;Bollywood composers who have succeeded to dabble magnificently in singles. After the immensely popular &lsquo;Zindagi Aa Raha Hoon&rsquo;, he delivered the melodious 'Chal Wahan Jaate Hai&rsquo;. His recently released track 'Main Rahoon Ya Na Rahoon&rsquo; has been incalculably loved by his admirers. He says,&ldquo;Success doesn&rsquo;t scare me but it comes with responsibility. I always try to do better than my last work and give my best.&rdquo;</p><figure data-orig-width="650" data-orig-height="433" class="tmblr-full"><img src="http://40.media.tumblr.com/b48bd5ffc37dc284f333389446382b95/tumblr_inline_o0jszlmXve1ta6vks_500.png" alt="image" data-orig-width="650" data-orig-height="433" width="500" height="333"></figure><p><br></p><p>Getting perhaps the finest starts for their vocation with Salman Khan&rsquo;s &lsquo;Jai Ho&rsquo;, there has been no looking back for Amal and Armaan Malik since then. With an affirmative outlook to the ubiquitous competition in the industry, the brother duo seems to have a prodigious future in the industry.<br></p><p>Sociofuzz wishes them all the best for the same.</p>
     """
}

from dbHandler import add , db, db1

# print db1['MovieBlog'].distinct('blogid')
# db['MovieBlog'].remove( { 'blogid' : 23 } )
# db1['MovieBlog'].remove( { 'blogid' : 23 } )

db['MovieBlog'].insert(a)
db1['MovieBlog'].insert(a)