"""
// ==UserScript==
// @name           TidyBox
// @namespace      http://squarefree.com/userscripts
// @description    Shrinks Tinderbox, letting you hover instead of scrolling to see information.  If you want to click a link in a popup, click to freeze the popup in place.
// @include        http://tinderbox.mozilla.org/*
// @author         Jesse Ruderman - http://www.squarefree.com/
// ==/UserScript==

// Version history:

// 2008-02-23     Initial release
// 2008-05-19     Updated for http://tinderbox.mozilla.org/showbuilds.cgi?tree=Mozilla2
// 2008-06-27     Detect "OS X" in addition to "Mac OS X".  Detect "leak test".
// 2008-11-23     Make it work on static pages and on the Camino page.  Add MIN_COLUMNS.
// 2009-02-04     Inline the log links and "add comment" button (contributed by Jonas Sicking)
//                  Also, add C links (contributed by Boris Zbarsky), and add links to the top-right.
// 2009-02-14     Fix a bug where the 'pushlog + tinderbox' link was missing on calm trees.
// 2009-08-08     Add 'M', 'E', 's', 'X' box types.
// 2009-08-18     Hide animated flames (patch from cjones).
// 2010-02-16     Update for split unit tests.  Show opt vs debug.  Fix animated-flame hiding.
"""
