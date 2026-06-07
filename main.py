import streamlit as st
import pandas as pd
import numpy as np
import os
import json
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns

plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

st.set_page_config(page_title="尖刀排小组积分管理系统", layout="wide")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "积分数据.json")
USER_DATA_FILE = os.path.join(BASE_DIR, "个人积分数据.json")
HISTORY_FILE = os.path.join(BASE_DIR, "积分变动历史.json")
CONFIG_FILE = os.path.join(BASE_DIR, "config.json")
WEEKLY_DATA_DIR = os.path.join(BASE_DIR, "历史周数据")

ADMIN_PASSWORD = "teacher123"

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"admin_password": ADMIN_PASSWORD}

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return pd.DataFrame(data)
    return pd.DataFrame(columns=['小组名称', '组长', '出勤积分', '单词打卡', '群分享', '期末学业', '单科状元', '总积分', '周次', '录入时间'])

def load_user_data():
    if os.path.exists(USER_DATA_FILE):
        with open(USER_DATA_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return pd.DataFrame(data)
    return pd.DataFrame(columns=['姓名', '小组名称', '出勤积分', '单词打卡', '群分享', '期末学业', '单科状元', '总积分', '周次', '录入时间'])

def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return pd.DataFrame(data)
    return pd.DataFrame(columns=['时间', '操作类型', '对象类型', '对象名称', '小组名称', '出勤变动', '单词变动', '分享变动', '学业变动', '状元变动', '总变动', '操作人'])

def save_data(df):
    os.makedirs(WEEKLY_DATA_DIR, exist_ok=True)
    data = df.to_dict('records')
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def save_user_data(df):
    os.makedirs(WEEKLY_DATA_DIR, exist_ok=True)
    data = df.to_dict('records')
    with open(USER_DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def save_history(df):
    data = df.to_dict('records')
    with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def add_history(operation_type, object_type, object_name, group_name, attendance=0, words=0, share=0, exam=0, top=0):
    history = load_history()
    new_row = pd.DataFrame({
        '时间': [datetime.now().strftime('%Y-%m-%d %H:%M:%S')],
        '操作类型': [operation_type],
        '对象类型': [object_type],
        '对象名称': [object_name],
        '小组名称': [group_name],
        '出勤变动': [attendance],
        '单词变动': [words],
        '分享变动': [share],
        '学业变动': [exam],
        '状元变动': [top],
        '总变动': [attendance + words + share + exam + top],
        '操作人': ['管理员']
    })
    history = pd.concat([history, new_row], ignore_index=True)
    save_history(history)

def calculate_total(row):
    return row['出勤积分'] + row['单词打卡'] + row['群分享'] + row['期末学业'] + row['单科状元']

def sync_group_scores(df, user_df):
    for group in df['小组名称'].unique():
        members = user_df[user_df['小组名称'] == group]
        df.loc[df['小组名称'] == group, '出勤积分'] = members['出勤积分'].sum()
        df.loc[df['小组名称'] == group, '单词打卡'] = members['单词打卡'].sum()
        df.loc[df['小组名称'] == group, '群分享'] = members['群分享'].sum()
        df.loc[df['小组名称'] == group, '期末学业'] = members['期末学业'].sum()
        df.loc[df['小组名称'] == group, '单科状元'] = members['单科状元'].sum()
        df.loc[df['小组名称'] == group, '总积分'] = members['总积分'].sum()
    return df

def main():
    if 'is_admin' not in st.session_state:
        st.session_state.is_admin = False
    if 'selected_group' not in st.session_state:
        st.session_state.selected_group = None
    if 'selected_user' not in st.session_state:
        st.session_state.selected_user = None
    if 'ai_tab' not in st.session_state:
        st.session_state.ai_tab = 'main'

    st.title("🔱 尖刀排小组积分管理系统")

    if not st.session_state.is_admin:
        with st.sidebar:
            st.subheader("管理员登录")
            password = st.text_input("密码", type="password", placeholder="请输入管理员密码")
            if st.button("登录", use_container_width=True):
                config = load_config()
                if password == config.get("admin_password", ADMIN_PASSWORD):
                    st.session_state.is_admin = True
                    st.success("登录成功！")
                    st.rerun()
                else:
                    st.error("密码错误，请重试")
        st.info("👋 欢迎查看尖刀排小组积分系统！\n\n管理员请在左侧输入密码登录以进行数据编辑操作。")

    df = load_data()
    user_df = load_user_data()
    history = load_history()

    if st.session_state.is_admin:
        with st.sidebar:
            st.subheader("🔐 管理员面板")
            st.success("✓ 已登录管理员账户")
            st.write("当前权限：可编辑、删除、清零数据")
            if st.button("退出登录", use_container_width=True, type="primary"):
                st.session_state.is_admin = False
                st.info("已安全退出管理员账户")
                st.rerun()

    if st.session_state.is_admin:
        tabs = st.tabs(["📊 小组数据", "👤 个人积分", "📈 统计排名", "🎨 可视化", "🤖 AI分析", "📋 积分明细", "⚙️ 成员管理"])
        tab1, tab2, tab3, tab4, tab5, tab6, tab7 = tabs
    else:
        tabs = st.tabs(["📊 小组数据", "👤 个人积分", "📈 统计排名", "🎨 可视化", "🤖 AI分析", "📋 积分明细"])
        tab1, tab2, tab3, tab4, tab5, tab6 = tabs

    with tab1:
        st.subheader("📊 小组数据管理")
        
        if not df.empty:
            st.dataframe(df)
            
            if st.session_state.is_admin:
                with st.expander("⚡ 积分清零", expanded=False):
                    col1, col2 = st.columns(2)
                    
                    if 'confirm_clear_all' not in st.session_state:
                        st.session_state.confirm_clear_all = False
                    
                    if not st.session_state.confirm_clear_all:
                        if col1.button("全部小组积分清零", type="primary", use_container_width=True):
                            st.session_state.confirm_clear_all = True
                    else:
                        col1.warning("⚠️ 确定要清零所有小组积分吗？此操作不可撤销！")
                        if col1.button("确认清零", type="primary", use_container_width=True):
                            df[['出勤积分', '单词打卡', '群分享', '期末学业', '单科状元', '总积分']] = 0
                            save_data(df)
                            add_history('清零', '小组', '全部小组', '全部', -df['出勤积分'].sum(), -df['单词打卡'].sum(), -df['群分享'].sum(), -df['期末学业'].sum(), -df['单科状元'].sum())
                            st.session_state.confirm_clear_all = False
                            st.success("已清零所有小组积分！")
                            st.rerun()
                        if col2.button("取消", use_container_width=True):
                            st.session_state.confirm_clear_all = False
        else:
            st.info("暂无小组数据")

    with tab2:
        st.subheader("👤 个人积分管理")
        
        if not user_df.empty:
            group_filter = st.selectbox("选择小组", ['全部'] + list(user_df['小组名称'].unique()))
            
            if group_filter == '全部':
                display_user_df = user_df
            else:
                display_user_df = user_df[user_df['小组名称'] == group_filter]
            
            st.dataframe(display_user_df[['姓名', '小组名称', '出勤积分', '单词打卡', '群分享', '期末学业', '单科状元', '总积分']])
            
            if st.session_state.is_admin:
                with st.expander("✏️ 修改个人积分", expanded=False):
                    selected_name = st.selectbox("选择成员", user_df['姓名'].unique())
                    member_data = user_df[user_df['姓名'] == selected_name].iloc[0]
                    
                    col1, col2, col3, col4, col5 = st.columns(5)
                    with col1:
                        attendance = st.number_input("出勤积分", value=member_data['出勤积分'], step=1)
                    with col2:
                        words = st.number_input("单词打卡", value=member_data['单词打卡'], step=1)
                    with col3:
                        share = st.number_input("群分享", value=member_data['群分享'], step=1)
                    with col4:
                        exam = st.number_input("期末学业", value=member_data['期末学业'], step=1)
                    with col5:
                        top = st.number_input("单科状元", value=member_data['单科状元'], step=1)
                    
                    if st.button("保存修改"):
                        idx = user_df[user_df['姓名'] == selected_name].index[0]
                        old_attendance = user_df.loc[idx, '出勤积分']
                        old_words = user_df.loc[idx, '单词打卡']
                        old_share = user_df.loc[idx, '群分享']
                        old_exam = user_df.loc[idx, '期末学业']
                        old_top = user_df.loc[idx, '单科状元']
                        
                        user_df.loc[idx, '出勤积分'] = attendance
                        user_df.loc[idx, '单词打卡'] = words
                        user_df.loc[idx, '群分享'] = share
                        user_df.loc[idx, '期末学业'] = exam
                        user_df.loc[idx, '单科状元'] = top
                        user_df.loc[idx, '总积分'] = calculate_total(user_df.loc[idx])
                        user_df.loc[idx, '录入时间'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        
                        save_user_data(user_df)
                        add_history('修改', '个人', selected_name, user_df.loc[idx, '小组名称'], 
                                   attendance - old_attendance, words - old_words, 
                                   share - old_share, exam - old_exam, top - old_top)
                        
                        df = sync_group_scores(df, user_df)
                        save_data(df)
                        
                        st.success(f"已更新 {selected_name} 的积分")
                        st.rerun()
                
                with st.expander("🗑️ 个人积分清零", expanded=False):
                    clear_name = st.selectbox("选择要清零的成员", user_df['姓名'].unique())
                    if st.button("清零该成员积分"):
                        idx = user_df[user_df['姓名'] == clear_name].index[0]
                        old_data = user_df.loc[idx].copy()
                        user_df.loc[idx, ['出勤积分', '单词打卡', '群分享', '期末学业', '单科状元', '总积分']] = 0
                        user_df.loc[idx, '录入时间'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        save_user_data(user_df)
                        add_history('清零', '个人', clear_name, user_df.loc[idx, '小组名称'], 
                                   -old_data['出勤积分'], -old_data['单词打卡'], 
                                   -old_data['群分享'], -old_data['期末学业'], -old_data['单科状元'])
                        
                        df = sync_group_scores(df, user_df)
                        save_data(df)
                        
                        st.success(f"已清零 {clear_name} 的积分")
                        st.rerun()
        else:
            st.info("暂无个人积分数据")

    with tab3:
        st.subheader("📈 统计排名")
        
        st.write("### 小组积分排名")
        if not df.empty:
            rank_df = df.copy()
            rank_df['排名'] = rank_df['总积分'].rank(ascending=False, method='min').astype(int)
            st.dataframe(rank_df[['排名', '小组名称', '组长', '总积分']].sort_values('排名'))
        else:
            st.info("暂无小组数据")
        
        st.write("### 个人积分排行榜")
        if not user_df.empty:
            user_rank_df = user_df.copy()
            user_rank_df['排名'] = user_rank_df['总积分'].rank(ascending=False, method='min').astype(int)
            user_rank_df = user_rank_df.sort_values('总积分')
            st.dataframe(user_rank_df[['排名', '姓名', '小组名称', '总积分']])
        else:
            st.info("暂无个人数据")

    with tab4:
        st.subheader("🎨 数据可视化分析")
        st.write("本页面提供多维度的数据可视化分析，帮助您直观了解积分分布和趋势")
        
        if df.empty:
            st.info("暂无数据")
        else:
            st.write("---")
            st.write("### 📊 一、小组层面分析")
            st.write("从整体角度分析各小组的积分表现和构成情况")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**1. 各组总积分排名**")
                st.write("📌 按总积分从高到低排序，直观展示各小组实力对比")
                fig, ax = plt.subplots(figsize=(10, 6))
                sorted_df = df.sort_values('总积分', ascending=False)
                palette = sns.color_palette('coolwarm', len(sorted_df))
                sns.barplot(x='总积分', y='小组名称', data=sorted_df, palette=palette, ax=ax)
                ax.set_xlabel('总积分', fontsize=12)
                ax.set_ylabel('小组名称', fontsize=12)
                ax.set_title('小组积分排名', fontsize=14, fontweight='bold')
                for i, v in enumerate(sorted_df['总积分']):
                    ax.text(v + 5, i, str(v), va='center')
                st.pyplot(fig)
                st.write(f"🏆 当前积分最高的小组：**{sorted_df.iloc[0]['小组名称']}组**（{sorted_df.iloc[0]['总积分']}分）")
                st.write(f"📊 小组平均积分：**{df['总积分'].mean():.1f}分**")
            
            with col2:
                st.write("**2. 积分分布饼图**")
                st.write("📌 展示各项积分在总体中的占比，了解积分来源结构")
                fig, ax = plt.subplots(figsize=(10, 6))
                total_points = df[['出勤积分', '单词打卡', '群分享', '期末学业', '单科状元']].sum()
                colors = ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF']
                ax.pie(total_points, labels=total_points.index, colors=colors, autopct='%1.1f%%', 
                       startangle=90, textprops={'fontsize': 10})
                ax.set_title('各项积分占比', fontsize=14, fontweight='bold')
                st.pyplot(fig)
                max_item = total_points.idxmax()
                min_item = total_points.idxmin()
                st.write(f"🔝 占比最高的积分项：**{max_item}**（{total_points[max_item]}分）")
                st.write(f"🔻 占比最低的积分项：**{min_item}**（{total_points[min_item]}分）")
            
            st.write("---")
            st.write("**3. 各组积分构成堆叠图**")
            st.write("📌 展示每个小组的积分构成详情，对比各组在不同维度的表现")
            fig, ax = plt.subplots(figsize=(14, 7))
            df_sorted = df.sort_values('总积分', ascending=False)
            df_sorted.set_index('小组名称')[['出勤积分', '单词打卡', '群分享', '期末学业', '单科状元']].plot(
                kind='bar', stacked=True, ax=ax, colormap='viridis'
            )
            ax.set_xlabel('小组名称', fontsize=12)
            ax.set_ylabel('积分', fontsize=12)
            ax.set_title('各组积分构成详情', fontsize=14, fontweight='bold')
            ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=10)
            plt.tight_layout()
            st.pyplot(fig)
            st.write("💡 **分析说明**：通过堆叠图可以看出每个小组的积分来源构成，识别优势和薄弱环节")
            
            st.write("**4. 各项积分对比箱线图**")
            st.write("📌 展示各项积分的分布范围、中位数和异常值，了解数据离散程度")
            fig, ax = plt.subplots(figsize=(14, 6))
            melt_df = df.melt(id_vars='小组名称', value_vars=['出勤积分', '单词打卡', '群分享', '期末学业', '单科状元'],
                             var_name='积分类型', value_name='积分值')
            sns.boxplot(x='积分类型', y='积分值', data=melt_df, palette='Set2', ax=ax)
            ax.set_xlabel('积分类型', fontsize=12)
            ax.set_ylabel('积分值', fontsize=12)
            ax.set_title('各项积分分布情况', fontsize=14, fontweight='bold')
            st.pyplot(fig)
            st.write("💡 **分析说明**：箱体表示数据的主要分布范围（25%-75%），横线为中位数，须线表示极值范围")
            
            st.write("---")
            st.write("### 👥 二、成员层面分析")
            st.write("深入分析每个小组内部成员的表现情况")
            
            selected_group = st.selectbox("🔍 选择小组查看成员详情", df['小组名称'].unique())
            group_users = user_df[user_df['小组名称'] == selected_group]
            
            if not group_users.empty:
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**{selected_group}组成员积分排行**")
                    st.write("📌 按积分从高到低展示小组成员排名")
                    fig, ax = plt.subplots(figsize=(10, 6))
                    sorted_users = group_users.sort_values('总积分', ascending=False)
                    sns.barplot(x='总积分', y='姓名', data=sorted_users, palette='Blues_r', ax=ax)
                    ax.set_xlabel('总积分', fontsize=12)
                    ax.set_ylabel('成员姓名', fontsize=12)
                    ax.set_title(f'{selected_group}组成员积分排名', fontsize=14, fontweight='bold')
                    for i, v in enumerate(sorted_users['总积分']):
                        ax.text(v + 2, i, str(v), va='center', fontsize=10)
                    st.pyplot(fig)
                    top_member = sorted_users.iloc[0]
                    st.write(f"🌟 小组积分最高：**{top_member['姓名']}**（{top_member['总积分']}分）")
                    st.write(f"👥 小组成员数：**{len(group_users)}人**")
                
                with col2:
                    st.write(f"**{selected_group}组成员积分构成**")
                    st.write("📌 展示小组整体在各项积分上的分配情况")
                    fig, ax = plt.subplots(figsize=(10, 6))
                    member_totals = group_users[['出勤积分', '单词打卡', '群分享', '期末学业', '单科状元']].sum()
                    colors = ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF']
                    ax.pie(member_totals, labels=member_totals.index, colors=colors, 
                           autopct='%1.1f%%', startangle=90, textprops={'fontsize': 9})
                    ax.set_title(f'{selected_group}组积分构成', fontsize=14, fontweight='bold')
                    st.pyplot(fig)
                    avg_points = group_users['总积分'].mean()
                    st.write(f"📊 小组平均积分：**{avg_points:.1f}分**")
                
                st.write(f"**{selected_group}组成员各项积分对比**")
                st.write("📌 对比每位成员在各项积分上的表现")
                fig, ax = plt.subplots(figsize=(14, 6))
                group_users.set_index('姓名')[['出勤积分', '单词打卡', '群分享', '期末学业', '单科状元']].plot(
                    kind='bar', ax=ax, colormap='tab20'
                )
                ax.set_xlabel('成员姓名', fontsize=12)
                ax.set_ylabel('积分', fontsize=12)
                ax.set_title(f'{selected_group}组成员各项积分详情', fontsize=14, fontweight='bold')
                ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=10)
                plt.tight_layout()
                st.pyplot(fig)
                st.write("💡 **分析说明**：可以看出每位成员的优势项目和需要提升的项目")
            else:
                st.info(f"{selected_group}组暂无成员数据")
            
            st.write("---")
            st.write("### 📈 三、综合分析")
            st.write("从宏观角度分析全体成员的数据特征和关系")
            
            st.write("**5. 全体成员积分分布直方图**")
            st.write("📌 展示全体成员积分的分布形态，了解整体水平")
            fig, ax = plt.subplots(figsize=(14, 6))
            sns.histplot(user_df['总积分'], bins=20, kde=True, color='#36A2EB', ax=ax)
            ax.axvline(user_df['总积分'].mean(), color='red', linestyle='--', 
                       label=f'平均值: {user_df["总积分"].mean():.1f}')
            ax.set_xlabel('积分值', fontsize=12)
            ax.set_ylabel('人数', fontsize=12)
            ax.set_title('全体成员积分分布', fontsize=14, fontweight='bold')
            ax.legend()
            st.pyplot(fig)
            st.write(f"👨‍🎓 学生总数：**{len(user_df)}人**")
            st.write(f"📊 平均积分：**{user_df['总积分'].mean():.1f}分**")
            st.write(f"📈 最高积分：**{user_df['总积分'].max()}分**")
            st.write(f"📉 最低积分：**{user_df['总积分'].min()}分**")
            
            st.write("**6. 各项积分相关性热图**")
            st.write("📌 分析各项积分之间的线性关系，识别关联性")
            corr = df[['出勤积分', '单词打卡', '群分享', '期末学业', '单科状元']].corr()
            fig, ax = plt.subplots(figsize=(10, 8))
            sns.heatmap(corr, annot=True, cmap='coolwarm', vmin=-1, vmax=1, 
                        square=True, ax=ax, annot_kws={'fontsize': 12})
            ax.set_title('各项积分相关性分析', fontsize=14, fontweight='bold')
            st.pyplot(fig)
            st.write("💡 **分析说明**：颜色越接近红色表示正相关越强（数值同时增减），越接近蓝色表示负相关越强")
            st.write("💡 **相关系数解读**：0.7以上为高度相关，0.3-0.7为中度相关，0.3以下为低度相关")
            
            st.write("---")
            st.write("### 📋 关键指标汇总")
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("小组总数", len(df))
            col2.metric("成员总数", len(user_df))
            col3.metric("平均小组积分", f"{df['总积分'].mean():.1f}")
            col4.metric("平均个人积分", f"{user_df['总积分'].mean():.1f}")

    with tab5:
        st.subheader("🤖 AI智能分析")
        
        if df.empty:
            st.info("暂无数据，请先录入积分")
        else:
            if st.session_state.ai_tab == 'main':
                st.write("请选择要查看的分析类型：")
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if st.button("📊 组与组之间分析", use_container_width=True, type="primary"):
                        st.session_state.ai_tab = 'group'
                        st.rerun()
                    st.write("比较各小组表现，划分梯队")
                
                with col2:
                    if st.button("👥 小组内成员分析", use_container_width=True, type="primary"):
                        st.session_state.ai_tab = 'member'
                        st.rerun()
                    st.write("分析每个小组内部成员情况")
                
                with col3:
                    if st.button("👨‍🎓 所有学生总体分析", use_container_width=True, type="primary"):
                        st.session_state.ai_tab = 'overall'
                        st.rerun()
                    st.write("全体学生积分数据汇总分析")
            
            elif st.session_state.ai_tab == 'group':
                st.subheader("📊 组与组之间分析")
                if st.button("← 返回"):
                    st.session_state.ai_tab = 'main'
                    st.rerun()
                
                try:
                    from sklearn.cluster import KMeans
                    from sklearn.preprocessing import StandardScaler
                    
                    stats_df = df.copy()
                    features = stats_df[['出勤积分', '单词打卡', '群分享', '期末学业', '单科状元']]
                    
                    scaler = StandardScaler()
                    scaled_features = scaler.fit_transform(features)
                    
                    kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
                    stats_df['梯队'] = kmeans.fit_predict(scaled_features)
                    
                    tier_names = ['待提升', '中等', '优秀']
                    
                    st.write("**1. 小组梯队划分**")
                    for tier in sorted(stats_df['梯队'].unique()):
                        tier_groups = stats_df[stats_df['梯队'] == tier]
                        st.write(f"**{tier_names[tier]}梯队** ({len(tier_groups)}个小组)")
                        st.dataframe(tier_groups[['小组名称', '组长', '总积分']])
                    
                    st.write("**2. 小组综合排名**")
                    stats_df['排名'] = stats_df['总积分'].rank(ascending=False, method='min').astype(int)
                    st.dataframe(stats_df[['排名', '小组名称', '组长', '总积分']].sort_values('排名'))
                    
                    st.write("**3. 各组强弱项对比**")
                    for _, row in stats_df.iterrows():
                        strengths = row[['出勤积分', '单词打卡', '群分享', '期末学业', '单科状元']].nlargest(2)
                        weaknesses = row[['出勤积分', '单词打卡', '群分享', '期末学业', '单科状元']].nsmallest(2)
                        st.write(f"**{row['小组名称']}** (组长: {row['组长']})")
                        st.write(f"  优势项: {', '.join(strengths.index)}")
                        st.write(f"  薄弱项: {', '.join(weaknesses.index)}")
                    
                    st.write("**4. 梯队提升建议**")
                    for tier in sorted(stats_df['梯队'].unique()):
                        st.write(f"### {tier_names[tier]}梯队")
                        if tier == 2:
                            st.write("""
                            - 保持现有优势，继续发挥榜样作用
                            - 可以结对帮扶其他梯队小组
                            - 挑战更高目标，争取单项突破
                            """)
                        elif tier == 1:
                            st.write("""
                            - 分析薄弱项，针对性加强
                            - 借鉴优秀小组经验
                            - 制定每周进步计划
                            """)
                        else:
                            st.write("""
                            - 重点提升出勤和单词打卡基础项
                            - 加强小组内部协作
                            - 设定短期目标，逐步提升
                            """)
                except Exception as e:
                    st.error(f"分析出错: {e}")
            
            elif st.session_state.ai_tab == 'member':
                st.subheader("👥 小组内成员分析")
                if st.button("← 返回"):
                    st.session_state.ai_tab = 'main'
                    st.rerun()
                
                if not user_df.empty:
                    group_list = df['小组名称'].unique()
                    
                    for group in group_list:
                        st.write(f"**{group}组 - 成员分析**")
                        members = user_df[user_df['小组名称'] == group]
                        
                        if not members.empty:
                            member_stats = members.copy()
                            member_stats['组内排名'] = member_stats['总积分'].rank(ascending=False, method='min').astype(int)
                            member_stats = member_stats.sort_values('组内排名')
                            
                            st.dataframe(member_stats[['组内排名', '姓名', '出勤积分', '单词打卡', '群分享', '期末学业', '单科状元', '总积分']])
                            
                            top_member = member_stats.iloc[0]
                            st.write(f"🌟 组内积分最高：{top_member['姓名']} ({top_member['总积分']}分)")
                            
                            avg_points = member_stats['总积分'].mean()
                            st.write(f"📊 组内平均积分：{round(avg_points, 1)}分")
                            
                            low_member = member_stats[member_stats['总积分'] < avg_points]
                            if len(low_member) > 0:
                                st.write(f"⚠️ 需要关注的成员（低于平均分）：{', '.join(low_member['姓名'].tolist())}")
                        else:
                            st.write("暂无成员数据")
                else:
                    st.info("暂无个人积分数据")
            
            elif st.session_state.ai_tab == 'overall':
                st.subheader("👨‍🎓 所有学生总体分析")
                if st.button("← 返回"):
                    st.session_state.ai_tab = 'main'
                    st.rerun()
                
                if not user_df.empty:
                    all_students = user_df.copy()
                    
                    st.write("**1. 全体学生积分分布**")
                    st.write(f"- 学生总数：{len(all_students)}人")
                    st.write(f"- 总积分范围：{all_students['总积分'].min()} - {all_students['总积分'].max()}分")
                    st.write(f"- 平均积分：{round(all_students['总积分'].mean(), 1)}分")
                    st.write(f"- 积分中位数：{all_students['总积分'].median()}分")
                    
                    st.write("**2. 各积分项总体统计**")
                    col1, col2, col3, col4, col5 = st.columns(5)
                    col1.metric("出勤积分", all_students['出勤积分'].sum())
                    col2.metric("单词打卡", all_students['单词打卡'].sum())
                    col3.metric("群分享", all_students['群分享'].sum())
                    col4.metric("期末学业", all_students['期末学业'].sum())
                    col5.metric("单科状元", all_students['单科状元'].sum())
                    
                    st.write("**3. 个人积分排行榜（前10名）**")
                    all_students['排名'] = all_students['总积分'].rank(ascending=False, method='min').astype(int)
                    top_students = all_students.sort_values('排名').head(10)
                    st.dataframe(top_students[['排名', '姓名', '小组名称', '总积分']])
                    
                    st.write("**4. 各积分项参与度分析**")
                    attendance_rate = len(all_students[all_students['出勤积分'] > 0]) / len(all_students) * 100
                    words_rate = len(all_students[all_students['单词打卡'] > 0]) / len(all_students) * 100
                    share_rate = len(all_students[all_students['群分享'] > 0]) / len(all_students) * 100
                    
                    st.write(f"- 出勤参与率：{round(attendance_rate, 1)}%")
                    st.write(f"- 单词打卡参与率：{round(words_rate, 1)}%")
                    st.write(f"- 群分享参与率：{round(share_rate, 1)}%")
                    
                    st.write("**5. 总体建议**")
                    if attendance_rate < 80:
                        st.write("⚠️ 建议：部分同学出勤打卡不够积极，需加强提醒")
                    if words_rate < 70:
                        st.write("⚠️ 建议：单词背诵打卡参与度较低，建议组织打卡活动")
                    if share_rate < 60:
                        st.write("⚠️ 建议：群分享活跃度不足，可鼓励同学分享学习心得")
                    
                else:
                    st.info("暂无个人积分数据")

    with tab6:
        st.subheader("📋 积分变动明细")
        
        if history.empty:
            st.info("暂无积分变动记录")
        else:
            st.dataframe(history)
            
            if st.session_state.is_admin and not history.empty:
                st.subheader("撤销操作")
                last_record = history.iloc[-1]
                
                st.write(f"最近一次操作：{last_record['操作类型']} - {last_record['对象名称']}")
                
                if st.button("撤销最近一次操作"):
                    obj_name = last_record['对象名称']
                    obj_type = last_record['对象类型']
                    group_name = last_record['小组名称']
                    
                    if obj_type == '个人':
                        idx = user_df[(user_df['姓名'] == obj_name) & (user_df['小组名称'] == group_name)].index[0]
                        user_df.loc[idx, '出勤积分'] -= last_record['出勤变动']
                        user_df.loc[idx, '单词打卡'] -= last_record['单词变动']
                        user_df.loc[idx, '群分享'] -= last_record['分享变动']
                        user_df.loc[idx, '期末学业'] -= last_record['学业变动']
                        user_df.loc[idx, '单科状元'] -= last_record['状元变动']
                        user_df.loc[idx, '总积分'] = calculate_total(user_df.loc[idx])
                        save_user_data(user_df)
                    elif obj_type == '小组':
                        if obj_name == '全部小组':
                            for idx in df.index:
                                df.loc[idx, '出勤积分'] -= last_record['出勤变动']
                                df.loc[idx, '单词打卡'] -= last_record['单词变动']
                                df.loc[idx, '群分享'] -= last_record['分享变动']
                                df.loc[idx, '期末学业'] -= last_record['学业变动']
                                df.loc[idx, '单科状元'] -= last_record['状元变动']
                                df.loc[idx, '总积分'] = calculate_total(df.loc[idx])
                        else:
                            idx = df[df['小组名称'] == obj_name].index[0]
                            df.loc[idx, '出勤积分'] -= last_record['出勤变动']
                            df.loc[idx, '单词打卡'] -= last_record['单词变动']
                            df.loc[idx, '群分享'] -= last_record['分享变动']
                            df.loc[idx, '期末学业'] -= last_record['学业变动']
                            df.loc[idx, '单科状元'] -= last_record['状元变动']
                            df.loc[idx, '总积分'] = calculate_total(df.loc[idx])
                        save_data(df)
                    
                    history = history.iloc[:-1]
                    save_history(history)
                    st.success("已撤销最近一次操作！")
                    st.rerun()

    if st.session_state.is_admin:
        with tab7:
            st.subheader("⚙️ 成员管理")
            
            st.write("---")
            st.subheader("添加新成员")
            if not df.empty:
                with st.form("add_member_form"):
                    col1, col2 = st.columns(2)
                    with col1:
                        new_name = st.text_input("姓名", placeholder="输入新成员姓名")
                    with col2:
                        new_group = st.selectbox("所属小组", df['小组名称'].unique())
                    
                    submitted = st.form_submit_button("添加成员")
                    if submitted:
                        if not new_name.strip():
                            st.error("请输入姓名")
                        elif new_name in user_df['姓名'].values:
                            st.error(f"{new_name} 已存在于系统中")
                        else:
                            new_row = pd.DataFrame({
                                '姓名': [new_name],
                                '小组名称': [new_group],
                                '出勤积分': [0],
                                '单词打卡': [0],
                                '群分享': [0],
                                '期末学业': [0],
                                '单科状元': [0],
                                '总积分': [0],
                                '周次': [1],
                                '录入时间': [datetime.now().strftime('%Y-%m-%d %H:%M:%S')]
                            })
                            user_df = pd.concat([user_df, new_row], ignore_index=True)
                            save_user_data(user_df)
                            add_history('新增', '个人', new_name, new_group, 0, 0, 0, 0, 0)
                            st.success(f"已成功添加成员：{new_name}")
                            st.rerun()
            else:
                st.info("请先在「小组数据」页面添加小组")
            
            st.write("---")
            st.subheader("调整成员小组")
            if 'move_success' not in st.session_state:
                st.session_state.move_success = False
            
            if st.session_state.move_success:
                st.success(st.session_state.move_message)
                st.session_state.move_success = False
            
            if not user_df.empty and len(df['小组名称'].unique()) > 1:
                col1, col2, col3 = st.columns(3)
                with col1:
                    move_name = st.selectbox("选择成员", user_df['姓名'].unique())
                with col2:
                    current_group = user_df[user_df['姓名'] == move_name]['小组名称'].iloc[0]
                    st.write(f"当前小组：{current_group}")
                with col3:
                    available_groups = [g for g in df['小组名称'].unique() if g != current_group]
                    new_group = st.selectbox("目标小组", available_groups)
                
                if st.button("调整小组"):
                    try:
                        idx = user_df[user_df['姓名'] == move_name].index[0]
                        old_group = user_df.loc[idx, '小组名称']
                        user_df.loc[idx, '小组名称'] = new_group
                        user_df.loc[idx, '录入时间'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        save_user_data(user_df)
                        add_history('调整', '个人', move_name, f"{old_group}→{new_group}", 0, 0, 0, 0, 0)
                        
                        df = sync_group_scores(df, user_df)
                        save_data(df)
                        
                        st.session_state.move_success = True
                        st.session_state.move_message = f"已将 {move_name} 从 {old_group} 调整到 {new_group}"
                        st.experimental_rerun()
                    except Exception as e:
                        st.error(f"调整失败：{str(e)}")
            else:
                st.info("需要至少2个小组和1个成员才能调整小组")
            
            st.write("---")
            st.subheader("删除成员")
            if not user_df.empty:
                delete_name = st.selectbox("选择要删除的成员", user_df['姓名'].unique())
                
                if 'confirm_delete' not in st.session_state:
                    st.session_state.confirm_delete = ""
                
                if st.session_state.confirm_delete != delete_name:
                    if st.button("删除成员"):
                        st.session_state.confirm_delete = delete_name
                else:
                    st.warning(f"⚠️ 确定要删除 {delete_name} 吗？此操作不可撤销！")
                    del_col1, del_col2 = st.columns(2)
                    if del_col1.button("确认删除"):
                        group_name = user_df[user_df['姓名'] == delete_name]['小组名称'].iloc[0]
                        user_df = user_df[user_df['姓名'] != delete_name]
                        save_user_data(user_df)
                        add_history('删除', '个人', delete_name, group_name, 0, 0, 0, 0, 0)
                        
                        df = sync_group_scores(df, user_df)
                        save_data(df)
                        
                        st.session_state.confirm_delete = ""
                        st.success(f"已删除成员：{delete_name}")
                        st.rerun()
                    if del_col2.button("取消"):
                        st.session_state.confirm_delete = ""
            else:
                st.info("暂无成员数据")
            
            st.write("---")
            st.subheader("成员列表")
            if not user_df.empty:
                filter_group = st.selectbox("按小组筛选", ['全部'] + list(df['小组名称'].unique()))
                
                if filter_group == '全部':
                    display_df = user_df[['姓名', '小组名称', '总积分']]
                else:
                    display_df = user_df[user_df['小组名称'] == filter_group][['姓名', '小组名称', '总积分']]
                
                st.dataframe(display_df)
            else:
                st.info("暂无成员数据")

if __name__ == "__main__":
    main()