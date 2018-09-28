import os
import pandas as pd
# from pandas import DataFrame
import re
from pyecharts import Line, Geo, Bar, Pie, Page, ThemeRiver
import pyecharts
from collections import Counter
import numpy as np
from snownlp import SnowNLP
import jieba
import matplotlib.pyplot as plt
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator


def data_draw(csv_file):
    page = Page(csv_file + ":按区域分析")
    d = pd.read_csv(csv_file, engine='python', encoding='utf-8')  # 读取CSV转为dataframe格式，并丢弃评论为空的的记录

    position_info = d['positionName'].value_counts()
    position_bar = pyecharts.Bar('职位信息柱状图')
    position_bar.add('职位', position_info.index, position_info.values, is_stack=True, is_label_show=True)
    position_bar.render(csv_file[:-4] + "_职位信息柱状图.html")  # 取CSV文件名的前8位数
    page.add_chart(position_bar)

    salary_info = salary_count(csv_file)
    salary_bar = pyecharts.Bar('月薪柱状图')
    salary_bar.add('月薪', list(salary_info.keys()), list(salary_info.values()), is_stack=True, is_label_show=True)
    salary_bar.render(csv_file[:-4] + "_月薪柱状图.html")  # 取CSV文件名的前8位数
    page.add_chart(salary_bar)

    data = industry_field_counts(csv_file)
    industry_field_pie = pyecharts.Pie("", "行业领域饼图", title_pos="right", width=1200, height=600)
    industry_field_pie.add("", list(data.keys()), list(data.values()), radius=[20, 50], label_text_color=None,
                           is_label_show=True,
                           legend_orient='vertical', is_more_utils=True, legend_pos='left')
    industry_field_pie.render(csv_file[:-4] + "_行业领域饼图.html")  # 取CSV文件名的前8位数
    page.add_chart(industry_field_pie)

    company_size_info = d['companySize'].value_counts()
    company_size_pie = pyecharts.Pie("", "公司规模饼图", title_pos="right", width=1200, height=600)
    company_size_pie.add("", company_size_info._index, company_size_info.values, radius=[20, 50], label_text_color=None,
                         is_label_show=True,
                         legend_orient='vertical', is_more_utils=True, legend_pos='left')
    company_size_pie.render(csv_file[:-4] + "_公司规模饼图.html")  # 取CSV文件名的前8位数
    page.add_chart(company_size_pie)

    finance_stage_info = d['financeStage'].value_counts()
    finance_stage_pie = pyecharts.Pie("", "公司融资阶段饼图", title_pos="right", width=1200, height=600)
    finance_stage_pie.add("", finance_stage_info._index, finance_stage_info.values, radius=[20, 50],
                          label_text_color=None,
                          is_label_show=True,
                          legend_orient='vertical', is_more_utils=True, legend_pos='left')
    finance_stage_pie.render(csv_file[:-4] + "_公司融资阶段饼图.html")  # 取CSV文件名的前8位数
    page.add_chart(finance_stage_pie)

    work_year_info = d['workYear'].value_counts()
    work_year_pie = pyecharts.Pie("", "职位工作经验饼图", title_pos="right", width=1200, height=600)
    work_year_pie.add("", work_year_info._index, work_year_info.values, radius=[20, 50], label_text_color=None,
                      is_label_show=True,
                      legend_orient='vertical', is_more_utils=True, legend_pos='left')
    work_year_pie.render(csv_file[:-4] + "_职位工作经验饼图.html")  # 取CSV文件名的前8位数
    page.add_chart(work_year_pie)

    education_info = d['education'].value_counts()
    education_pie = pyecharts.Pie("", "职位学历要求饼图", title_pos="right", width=1200, height=600)
    education_pie.add("", education_info._index, education_info.values, radius=[20, 50], label_text_color=None,
                      is_label_show=True,
                      legend_orient='vertical', is_more_utils=True, legend_pos='left')
    education_pie.render(csv_file + "_职位学历要求饼图.html")  # 取CSV文件名的前8位数
    page.add_chart(education_pie)

    page.render(csv_file[:-4] + "_工作分析汇总.html")


def draw_district_pic(csv_file):
    page = Page(csv_file + ":城市区域职位分析")
    d = pd.read_csv(csv_file, engine='python', encoding='utf-8')  # 读取CSV转为dataframe格式，并丢弃评论为空的的记录

    district_info = d['district'].value_counts()
    geo1 = Geo("", "城市区域职位分布", title_pos="center", width=1200, height=600,
               background_color='#404a59', title_color="#fff")
    geo1.add("", district_info.index, district_info.values, maptype="广州", visual_range=[0, 300],
             visual_text_color="#fff", is_geo_effect_show=False,
             is_piecewise=True, visual_split_number=10, symbol_size=15, is_visualmap=True, is_more_utils=True)
    geo1.render(csv_file[:-4] + "_城市区域职位dotmap.html")
    page.add_chart(geo1)

    district_pie = pyecharts.Pie("", "区域职位饼图", title_pos="right", width=1200, height=600)
    district_pie.add("", district_info._index, district_info.values, radius=[20, 50], label_text_color=None,
                     is_label_show=True,
                     legend_orient='vertical', is_more_utils=True, legend_pos='left')
    district_pie.render(csv_file[:-4] + "_区域职位饼图.html")  # 取CSV文件名的前8位数
    page.add_chart(district_pie)

    page.render(csv_file + "_城市区域分析汇总.html")


def draw_city_pic(csv_file):
    page = Page(csv_file + ":城市职位分析")
    d = pd.read_csv(csv_file, engine='python', encoding='utf-8')  # 读取CSV转为dataframe格式，并丢弃评论为空的的记录
    city_info = d['city'].value_counts()
    geo = Geo("", "城市职位分布", title_pos="center", width=1200, height=600,
              background_color='#404a59', title_color="#fff")
    geo.add("", city_info.index, city_info.values, maptype="china", visual_range=[1, 200], visual_text_color="#fff",
            is_geo_effect_show=False,
            is_piecewise=True, visual_split_number=10, symbol_size=15, is_visualmap=True, is_more_utils=True)
    geo.render(csv_file[:-4] + "_城市职位dotmap.html")
    page.add_chart(geo)

    geo2 = Geo("", "城市职位热力图", title_pos="center", width=1200, height=600, background_color='#404a59',
               title_color="#fff", )
    geo2.add("", city_info.index, city_info.values, type="heatmap", is_visualmap=True, visual_range=[1, 200],
             visual_text_color='#fff', is_more_utils=True)
    geo2.render(csv_file[:-4] + "_城市职位heatmap.html")  # 取CSV文件名的前8位数
    page.add_chart(geo2)

    city_pie = pyecharts.Pie("", "城市职位饼图", title_pos="right", width=1200, height=600)
    city_pie.add("", city_info.index, city_info.values, radius=[20, 50], label_text_color=None, is_label_show=True,
                 legend_orient='vertical', is_more_utils=True, legend_pos='left')
    city_pie.render(csv_file[:-4] + "_城市职位饼图.html")  # 取CSV文件名的前8位数
    page.add_chart(city_pie)

    page.render(csv_file[:-4] + "_城市分析汇总.html")


def industry_field_counts(csv_file):
    industry_fields = []
    d = pd.read_csv(csv_file, engine='python', encoding='utf-8')
    info = d['industryField']
    for i in range(len(info)):
        # print("data:%d %s"%(i,info[i]))
        try:
            data = re.split('[,、 ]', info[i])
        except:
            continue
        for j in range(len(data)):
            industry_fields.append(data[j])
    counts = Counter(industry_fields)
    return counts


def salary_count(csv_file):
    salary_dict = {'2k以下': 0, '2k-5k': 0, '5k-10k': 0, '10k-15k': 0, '15k-25k': 0, '25k-50k': 0, '50k以上': 0}
    d = pd.read_csv(csv_file, engine='python', encoding='utf-8')
    salaries = d['salary'].values
    return salary_categorize(salaries)


def salary_categorize(salarys):
    salary_dict = {'2k以下': 0, '2k-5k': 0, '5k-10k': 0, '10k-15k': 0, '15k-25k': 0, '25k-50k': 0, '50k以上': 0}
    for salary in salarys:
        if re.match('^[0-1]k-*|.*-[0-1]k$', salary) != None:
            salary_dict['2k以下'] += 1
        if re.match('^[2-4]k-*|.*-[2-4]k$', salary) != None:
            salary_dict['2k-5k'] += 1
        if re.match('^[5-9]k-*|.*-[5-9]k$', salary) != None:
            salary_dict['5k-10k'] += 1
        if re.match('^1[0-4]k-*|.*-1[0-4]k$', salary) != None:
            salary_dict['10k-15k'] += 1
        if re.match('^1[5-9]k-*|^2[0-4]k-*|.*-1[5-9]k$|.*-2[0-4]k$', salary) != None:
            salary_dict['15k-25k'] += 1
        if re.match('^2[5-9]k-*|^[3-4][0-9]k-*|.*-2[5-9]k$|.*-[3-4][0-9]k$', salary) != None:
            salary_dict['25k-50k'] += 1
        if re.match('^[5-9][0-9]k-*|.*-[5-9][0-9]k$|^\d{3,}k-*|.*-\d{3,}k$', salary) != None:
            salary_dict['50k以上'] += 1
    return salary_dict


def draw_salary_work_year(csv_file):
    bar = Bar("", height=720, width=1200, title_pos="65%")
    d = pd.read_csv(csv_file, engine='python', encoding='utf-8')[['workYear', 'salary']]
    work_years = d['workYear'].drop_duplicates().values
    for y in work_years:
        print("work year %s" % y)
        salarys = d[d.workYear == y]['salary'].values
        dict = salary_categorize(salarys)
        print(dict)
        bar.add(y, list(dict.keys()), list(dict.values()), is_stack=True)
    bar.render(csv_file[:-4] + "_月薪工作经验柱状图.html")


def word_cloud(csv_file, stopwords_path, pic_path):
    pic_name = csv_file[:-4] + "_词云图.png"
    d = pd.read_csv(csv_file, engine='python', encoding='utf-8')
    content = d['job_desc'].values
    comment_after_split = jieba.cut(str(content), cut_all=False)
    wl_space_split = " ".join(comment_after_split)
    background_image = plt.imread(pic_path)
    stopwords = STOPWORDS.copy()
    with open(stopwords_path, 'r', encoding='utf-8') as f:
        for i in f.readlines():
            stopwords.add(i.strip('\n'))
        f.close()

    wc = WordCloud(width=1024, height=768, background_color='white',
                   mask=background_image, font_path="simhei.ttf",
                   stopwords=stopwords, max_font_size=400,
                   random_state=50)
    wc.generate_from_text(wl_space_split)
    img_colors = ImageColorGenerator(background_image)
    wc.recolor(color_func=img_colors)
    plt.imshow(wc)
    plt.axis('off')
    plt.show()
    wc.to_file(pic_name)


def main(csv_file, stopwords_path, pic_path):
    path = os.path.abspath(os.curdir)
    csv_file = path + "/" + csv_file + ".csv"
    data_draw(csv_file)
    industry_field_counts(csv_file)
    # draw_district_pic(csv_file)
    draw_city_pic(csv_file)
    # word_cloud(csv_file, stopwords_path, pic_path)
    draw_salary_work_year(csv_file)


if __name__ == '__main__':
    # main("邪不压正", "stopwords_1.txt", "jiangwen.jpg")
    # main("我不是药神", "stopwords_2.txt", "xuzheng.jpg" )
    # main("霸王别姬", "stopwords_3.txt", "霸王别姬.jpg" )
    # main("杀死一只知更鸟", "stopwords_3.txt", "霸王别姬.jpg" )
    # main("lagou-广州-Python", "stopwords_4.txt", "python_logo.jpg" )
    main("lagou-全国-Python", "stopwords_4.txt", "python_logo.jpg")
    # main("lagou-广州-测试", "stopwords_4.txt", "xuzheng.jpg")
