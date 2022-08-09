# FINA4350 WSB Sentiment and Stock Returns
By Simplicity

# Overview
This project aims to analyze the correlation between the sentiment of r/wallstreetbets posts and stock returns. By posts, we mean we will analyze the title, content, and the highest upvoted comment. Since there are a lot of images used, when analyzing the posts individually, we realized that the highest upvoted comment will often be taking about the image. We also wanted to identify what stock the post is talking about, conduct sentiment analysis on it using VADER, and then visualize the correlation.

# Steps
1. [Data Sourcing Reddit Posts](https://buehlmaier.github.io/FINA4350-student-blog-2022-01/project-introduction-and-step-1-data-collecting-and-storage-group-simplicity.html)
2. [Cleaning Data and Identifying Stock](https://buehlmaier.github.io/FINA4350-student-blog-2022-01/cleaning-data-and-identifying-stock-group-simplicity.html)
3. [Conducting Sentiment Analysis and Metric Incorporation](https://buehlmaier.github.io/FINA4350-student-blog-2022-01/sentiment-analysis-and-metric-incorporation-group-simplicity.html)
4. [Visualizing Correlation and Prediction](https://buehlmaier.github.io/FINA4350-student-blog-2022-01/correlation-analysis-group-simplicity.html)

# Short Conclusion
In short, there is a very low correlation between r/WSB sentiment and stock returns. Basically, it means that if there is a strong sentiment (with incorporated upvotes, comments that emphasizes the score), the stock return will not be greatly or significantly positive (sometimes even negative!), and vice versa. When conducting our extension via back-testing, if we were to follow the sentiment score produced and traded based on that score, we would ultimately lose money. However, if we did the reverse, meaning if the score was more positive indicating a stronger buy, and we sell instead, then we would actually profit! This may actually feed into the conspiracy that stronger financial players are playing WSB like Belfort playing wolf.
