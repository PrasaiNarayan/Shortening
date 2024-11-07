import pandas as pd
from datetime import timedelta
import math

from Provider import Data_provider,Stretch_Flag_setter,Date_Class
import schedule_manage
import pandas as pd
import jaconv


# Function to correct values
def correct_string(value):
    if isinstance(value, str):
        # Convert full-width to half-width, except for Katakana
        value = jaconv.z2h(value, kana=False)
        # Replace specific patterns like ｼﾖ- with ｼｮｰ
        value = value.replace('ｼﾖ-', 'ｼｮｰ')
    return value

#this is data of how far ahead you wanna plan
see_future=3
#these are planning lines currently there are two lines
line_names=['SV','SP']
#this is date range you wanna plan . starting to end date
# dat=pd.date_range(start='06/09/2022', end='06/29/2022')

dat=pd.date_range(start='03/01/2024', end='03/15/2024')

# Read the CSV files 
#these csv files are input for the planning 
# df_input = pd.read_csv("data.csv", encoding="utf-8_sig")
df_input = pd.read_csv("shortening_3-5-order_data_2024_3_月.csv", encoding="cp932")
#Shortening_order_data_2024_3-5_月.csv
master = pd.read_csv("master.csv", encoding="utf-8_sig")

#creating date range 
dates=[]
for ele in dat:
    if ele.day_name()!='Sunday' and ele.day_name()!='Saturday':
        dates.append(ele)

# print(dates)
# exit()
#Addition of code for handaling artificial brakes

dates_with_features=[]
for ele in dates:
    #user defined break
    #this is the brake that user will include and it can be multiple and has different durations
    long_break_start_time=[]#[ele+timedelta(hours=11)+timedelta(minutes=30)]
    break_duration=[]#[60]
    line_break_pattern={}
    line_break_pattern['break_pattern']={}

    for index,each_brake in enumerate(long_break_start_time):
        if 'break_pattern' not in line_break_pattern:
            line_break_pattern['break_pattern']={}
        line_break_pattern['break_pattern'][f'break{index}']={'break':each_brake,f'break_duration':break_duration[index]}

    each_date_feature=Date_Class(ele,line_break_pattern)
    dates_with_features.append(each_date_feature)

# Convert both '品目コード' columns to string (object) type before merging
df_input['品目コード'] = df_input['品目コード'].astype(str)
master['品目コード'] = master['品目コード'].astype(str)

# Identify the '品目コード' in df_input that are not in master
not_in_master = df_input[~df_input['品目コード'].isin(master['品目コード'])]

# Optionally, you can write this list to a CSV file
not_in_master['品目コード'].to_csv('not_in_master.csv', encoding='utf-8_sig', index=False)

# Perform the merge and add suffixes to overlapping columns (for columns in df_input)
df = pd.merge(df_input, master, on='品目コード', how='inner', suffixes=('_input', ''))

# Drop the columns from df_input that are duplicated in master
df = df.loc[:, ~df.columns.str.endswith('_input')]

df = df.applymap(lambda x: jaconv.z2h(x, kana=True) if isinstance(x, str) else x)

df = df.applymap(correct_string)

df.to_csv('merged.csv',encoding='utf-8_sig',index=False)
# exit()
df_moto=df.copy(deep=True)

#addition of extra columns
df['納期'] = pd.to_datetime(df['納期'],format='%Y%m%d')
df['納期_copy']=df['納期']
df['firsts']=0
df['lasts']=0
df['last_first']=0
df['time_taken']=0
df['SV_time_taken']=0
df['SP_time_taken']=0
df['no_renzoku_seisan']=0
df['clean_time']=0
df['kouyousoka_maya']=0
df['arerukon_maya']=0
df['weight_limit']=0
df['only_two']=0
df['mc_renzo']=0  #for mcショット
df["stretch_flag"]=0


Class_Data=[]

    

for ind,row in df.iterrows():
    # print(row.予定数量)
    # print(row['SV流量(㎏/h)'])
    if row.SVライン=='〇' and row['SV流量(㎏/h)']!='-' and row.荷姿=='C/S':
        time_SV= math.ceil(row['予定数量(㎏)'] / int(row['SV流量(㎏/h)'].replace(',', ''))*60)
        df.at[ind,'SV_time_taken']=time_SV

    else:
        df.at[ind,'SV_time_taken']=0

    if row.SPライン=='〇' and row['SP流量(㎏/h)']!='-' and row.荷姿=='CAN':
        time_SP= math.ceil(row['予定数量(㎏)'] / int(row['SP流量(㎏/h)'].replace(',', ''))*60)
        df.at[ind,'SP_time_taken']=time_SP

    else:
        df.at[ind,'SP_time_taken']=0

    # time_t=math.ceil(row.予定数量/row.流速*60)
    # df.at[ind,'time_taken']=time_t
    
    if row.テンパリング=='〇':
        day=row.納期_copy.day_name()
     
        # print(day)
        if day=='Monday':
            deltas=row.納期_copy-timedelta(days=3)
        elif day=='Sunday':
            deltas=row.納期_copy-timedelta(days=2)
        else:
            deltas=row.納期_copy-timedelta(days=1)
        # print(deltas)
        df.at[ind,'納期_copy']=deltas
        df.at[ind,'weight_limit']=1  
  
    if row.リパック=='〇':

        day=row.納期_copy.day_name()
        if day=='Sunday':
            delt=row.納期_copy-timedelta(days=9)
        if day=='Saturday':
            delt=row.納期_copy-timedelta(days=8)
        else:
            delt=row.納期_copy-timedelta(days=7)
        df.at[ind,'納期_copy']=delt
        df.at[ind,'stretch_flag']=1
    

    if row.沃素価=='高': #done
        df.at[ind,'lasts']=1
        df.at[ind,'no_renzoku_seisan']=1

    if row.沃素価=='準高': #done
        df.at[ind,'last_first']=1
        df.at[ind,'kouyousoka_maya']=1

    if row.沃素価=='低':#done
        df.at[ind,'last_first']=1

    if row.KI製品=='○':#done
        df.at[ind,'firsts']=1
        df.at[ind,'clean_time']=1

    if row['MO-7S配合']=='○':#doneMO-7S添加品
        df.at[ind,'lasts']=1
        df.at[ind,'arerukon_maya']=1

    # if row.備考=='副原料添加なし初回限定':#done
    if isinstance(row.特記事項, str) and row.特記事項.startswith('副原料無添加品'):
        df.at[ind,'firsts']=1
        df.at[ind,'特記事項']='副原料無添'

    # if row.備考=='初回限定':#done
    # if row.特記事項.startswith('初回限定'):
    #     df.at[ind,'firsts']=1
    #     df.at[ind,'no_renzoku_seisan']=1

    if row.初回限定 == '〇' and (pd.isna(row.特記事項) or not row.特記事項.startswith('副原料無添加品')) and not row.品名.startswith('MCｼｮｰﾄ'):

        df.at[ind,'特記事項']='初回限定'
        df.at[ind,'firsts']=1
        df.at[ind,'no_renzoku_seisan']=1


    if row.品名=='ｲﾄｳIK-NT(H)' or row.品名=='ﾊﾟﾈﾘ-PV(13)':
        df.at[ind,'mc_renzo']=1


    if row.アレルゲン=='B':#done
        df.at[ind,'lasts']=1

    if row.品名.startswith('MCｼｮｰﾄ'):#done
        df.at[ind,'firsts']=1
        df.at[ind,'only_two']=1

    if row.品名=='ﾌﾟﾚﾐｱﾑｼﾖ-ﾄ-CF(S)':#done
        df.at[ind,'firsts']=1


    if row.最終限定=='〇' :
        df.at[ind,'lasts']=1

for ind,row in df.iterrows():
    day=row.納期.day_name()
    if day=='Saturday':
        deltas=row.納期-timedelta(days=1)
        df.at[ind,'納期_copy']=deltas
    elif day=='Sunday':
        deltas=row.納期-timedelta(days=2)
        df.at[ind,'納期_copy']=deltas

for ind,row in df.iterrows():
    if row.品名.startswith('ﾊﾟﾈﾘ-ｼｮｰﾄST-2'):
        if row.納期_copy.day_name()=='Wednesday':
            deltas=row.納期_copy-timedelta(days=1)
            df.at[ind,'納期_copy']=deltas
        
        if row.納期_copy.day_name()=='Thursday':
            deltas=row.納期_copy-timedelta(days=2)
            df.at[ind,'納期_copy']=deltas

        if row.納期_copy.day_name()=='Friday':
            deltas=row.納期_copy-timedelta(days=3)
            df.at[ind,'納期_copy']=deltas

        if row.納期_copy.day_name()=='Saturday':
            deltas=row.納期_copy-timedelta(days=4)
            df.at[ind,'納期_copy']=deltas
        
        if row.納期_copy.day_name()=='Sunday':
            deltas=row.納期_copy-timedelta(days=5)
            df.at[ind,'納期_copy']=deltas
        

df.to_csv("data_with_features.csv",encoding="utf-8_sig",index=False)

for ind,row in df.iterrows():
    class_data=Data_provider(row.品目コード,
                             row.品名,
                             None,#row.ライン,
                             None,#row.ライン名,
                             row.入目,
                             None,#row.流速,
                             row.テンパリング,
                             row.沃素価,
                             row.KI製品,
                             row.初回限定,
                             row.最終限定,
                             row.リパック,
                             row['予定数量(㎏)'],#row.予定数量,
                             row.納期,
                             row['チケットＮＯ'],
                             row.特記事項,
                             row['MO-7S配合'],
                             row.アレルゲン,
                             None,#row.生産日,
                             None,#row.順番,
                             None,#row.slot,
                             row.SV_time_taken,
                             row.SP_time_taken,
                             row.納期_copy,
                             row.firsts,
                             row.no_renzoku_seisan,
                             row.clean_time,
                             row.kouyousoka_maya,
                             row.lasts,
                             row.last_first,
                             row.weight_limit,
                             row.only_two,
                             row.mc_renzo,
                             row.stretch_flag,
                             row.窒素ガス,
                             row['SP流量(㎏/h)'],
                             row['SV流量(㎏/h)'],
                             row.荷姿,
                             used=0,
                             cleaning_jikan=0,
                            #  
                             
                            #  next_renzoku=True

    )
    Class_Data.append(class_data)



df=df.sort_values(by="納期_copy")
df["used"]=0

count=0

final_df=pd.DataFrame(columns=df_moto.columns)
final_df1=pd.DataFrame(columns=df_moto.columns)
final_df2=pd.DataFrame(columns=df_moto.columns)



flag_object=[]

# this region creates instances for the dates along with the flags
for ele in dates:
    ibj1= Stretch_Flag_setter(ele,see_future)
    flag_object.append(ibj1)

        
# final_df,Class_Data=schedule_manage.schedule_manager(Class_Data,dates,final_df,flag_object,see_future)
final_df_SV,final_df_SP,Class_Data=schedule_manage.schedule_manager(Class_Data,dates_with_features,final_df,flag_object,see_future,line_names)
# final_df,Class_Data=new_schedule_manage.schedule_manager(Class_Data,dates_with_features,final_df,flag_object,see_future)
final_df_SV.to_csv("output_SV.csv",encoding="utf-8_sig",index=False)
final_df_SP.to_csv("output_SP.csv",encoding="utf-8_sig",index=False)


non_final_df=pd.DataFrame(columns=df_moto.columns)
non_final_df2=pd.DataFrame(columns=df_moto.columns)
abc="first_planning"

unused_class_data=schedule_manage.unused_dataframe(Class_Data,non_final_df,abc)
# unused_class_data=new_schedule_manage.unused_dataframe(Class_Data,non_final_df,abc)
unused_object_lists=[]

for ele in Class_Data:
    if ele.get_used()==0:
        unused_object_lists.append(ele)




# if len(unused_object_lists)>0:
#     abc="second_planning"
#     print("the first unused date")
#     first_unused_date=unused_object_lists[0].get_nouki_copy()



#     print(first_unused_date.day_name())

#     if first_unused_date.day_name()=='Sunday':
#         usable_saturday=first_unused_date-timedelta(days=1)

#     elif first_unused_date.day_name()=='Monday':
#         usable_saturday=first_unused_date-timedelta(days=2)

#     elif first_unused_date.day_name()=='Tuesday':
#         usable_saturday=first_unused_date-timedelta(days=3)

#     elif first_unused_date.day_name()=='Wednesday':
#         usable_saturday=first_unused_date-timedelta(days=4)

#     elif first_unused_date.day_name()=='Thursday':
#         usable_saturday=first_unused_date-timedelta(days=5)
    
#     elif first_unused_date.day_name()=='Friday':
#         usable_saturday=first_unused_date-timedelta(days=6)

    
#     for ele in Class_Data:
#         print(ele.get_nouki(),usable_saturday)
#         if ele.get_nouki()==usable_saturday or ele.get_nouki()-timedelta(days=1)==usable_saturday:
#             print("this is executing")
#             # if ele.get_nouki_copy()!=first_unused_date:
#             ele.set_nouki_copy(usable_saturday)
#                 # print(ele.get_nouki(),ele.get_nouki_copy())
        

#         elif ele.get_tenpahin()=='〇' and (ele.get_nouki()-timedelta(days=1)==usable_saturday or ele.get_nouki()-timedelta(days=2)==usable_saturday):
#             ele.set_nouki_copy(usable_saturday)

#     dates.append(usable_saturday)
#     dates.sort()


#     flag_object.clear()
#     for ele in dates:
#         ibj1= Stretch_Flag_setter(ele,see_future)
#         flag_object.append(ibj1)


#     for ele in Class_Data:
#         ele.set_used(0)
#         # ele.set_end_time(ele.get_nouki_copy()-timedelta(days=1))
#         ele.set_st_time(None)
#         ele.set_jyounban(None)
#         ele.set_slot_removing(None)
#         ele.set_seisanbi(None)
#         ele.set_st_time(None)


#     dates_with_features=[]
#     #Addition of code for handaling artificial brakes
#     for ele in dates:
#         #user defined break
#         #this is the brake that user will include and it can be multiple and has different durations
#         long_break_start_time=[]#[ele+timedelta(hours=11)+timedelta(minutes=30)]
#         break_duration=[]#[60]
#         line_break_pattern={}
#         line_break_pattern['break_pattern']={}

#         for index,each_brake in enumerate(long_break_start_time):
#             if 'break_pattern' not in line_break_pattern:
#                 line_break_pattern['break_pattern']={}
#             line_break_pattern['break_pattern'][f'break{index}']={'break':each_brake,f'break_duration':break_duration[index]}

#         each_date_feature=Date_Class(ele,line_break_pattern)
#         dates_with_features.append(each_date_feature)


    
#     # final_df,Class_Data=schedule_manage.schedule_manager(Class_Data,dates,final_df1,flag_object,see_future)
#     final_df_SV,final_df_SP,Class_Data=schedule_manage.schedule_manager(Class_Data,dates_with_features,final_df1,flag_object,see_future,line_names)
#     # final_df,Class_Data=new_schedule_manage.schedule_manager(Class_Data,dates_with_features,final_df1,flag_object,see_future)
#     final_df_SV.to_csv("output_SV.csv",encoding="utf-8_sig",index=False)
#     final_df_SP.to_csv("output_SP.csv",encoding="utf-8_sig",index=False)
#     # unused_class_data=new_schedule_manage.unused_dataframe(Class_Data,non_final_df2,abc)
#     unused_class_data=schedule_manage.unused_dataframe(Class_Data,non_final_df2,abc)


# special_case.special_function(Class_Data,final_df2)


    