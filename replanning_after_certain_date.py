
import pandas as pd
from datetime import date, timedelta
import math
from Provider import Data_provider
import Record_finder
from Provider import Stretch_Flag_setter
from special_records import one_day_replanner,unused_dataframe
from schedule_manage import schedule_manager


def func_get_all_variables(speciial_records):
   
    speciial_records['納期_copy']=speciial_records['納期']
    speciial_records['firsts']=0
    speciial_records['lasts']=0
    speciial_records['last_first']=0
    speciial_records['time_taken']=0
    speciial_records['no_renzoku_seisan']=0
    speciial_records['clean_time']=0
    speciial_records['kouyousoka_maya']=0
    speciial_records['arerukon_maya']=0
    speciial_records['weight_limit']=0
    speciial_records['only_two']=0
    speciial_records['mc_renzo']=0
    speciial_records["stretch_flag"]=0

    for ind,row in speciial_records.iterrows():
        time_t=math.ceil(row.予定数量/row.流速*60)
        speciial_records.at[ind,'time_taken']=time_t

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
            speciial_records.at[ind,'納期_copy']=deltas
            speciial_records.at[ind,'weight_limit']=1  

        if row.リパック=='〇':

            day=row.納期_copy.day_name()
            if day=='Sunday':
                delt=row.納期_copy-timedelta(days=9)
            if day=='Saturday':
                delt=row.納期_copy-timedelta(days=8)
            else:
                delt=row.納期_copy-timedelta(days=7)
            speciial_records.at[ind,'納期_copy']=delt
            speciial_records.at[ind,'stretch_flag']=1
        
        # if row.初回限定=='〇':#done
        #     special_data_of_given_day.at[ind,'firsts']=1
        #     special_data_of_given_day.at[ind,'no_renzoku_seisan']=1

        if row.沃素価=='高沃素価': #done
            speciial_records.at[ind,'lasts']=1
            speciial_records.at[ind,'no_renzoku_seisan']=1

        if row.沃素価=='準高沃素価': #done
            speciial_records.at[ind,'last_first']=1
            speciial_records.at[ind,'kouyousoka_maya']=1

        if row.沃素価=='低沃素価':#done
            speciial_records.at[ind,'last_first']=1

        if row.KI製品=='○':#done
            speciial_records.at[ind,'firsts']=1
            speciial_records.at[ind,'clean_time']=1

        if row.備考=='MO-7S添加品':#done
            speciial_records.at[ind,'lasts']=1
            speciial_records.at[ind,'arerukon_maya']=1

        if row.備考=='副原料添加なし初回限定':#done
            speciial_records.at[ind,'firsts']=1

        if row.備考=='初回限定':#done
            speciial_records.at[ind,'firsts']=1
            speciial_records.at[ind,'no_renzoku_seisan']=1

        if row.品名=='ｲﾄｳIK-NT(H)' or row.品名=='ﾊﾟﾈﾘ-PV(13)':
            speciial_records.at[ind,'mc_renzo']=1


        if row.アレルゲン=='B':#done
            speciial_records.at[ind,'lasts']=1

        if row.品名.startswith('MCｼｮｰﾄ'):#done
            speciial_records.at[ind,'firsts']=1
            speciial_records.at[ind,'only_two']=1

        if row.品名=='ﾌﾟﾚﾐｱﾑｼﾖ-ﾄ-CF(S)':#done
            speciial_records.at[ind,'firsts']=1


        if row.最終限定=='〇' :
            speciial_records.at[ind,'lasts']=1


    return speciial_records


def remaining_planner(unused_class_data,used_class_data):
    speciial_records=pd.read_csv("select_data.csv",encoding="utf-8_sig")
    speciial_records['納期'] = pd.to_datetime(speciial_records['納期'],format='%Y%m%d')  
    speciial_records= func_get_all_variables(speciial_records)
    date_list=speciial_records['納期_copy'].tolist()[-1]

    output_file=pd.read_csv("output1.csv",encoding="utf-8_sig")
    output_file["生産日"]=pd.to_datetime(output_file["生産日"],format='%Y-%m-%d')
    output_file_backup=output_file

    output_file_backup=output_file_backup[output_file_backup["生産日"]<=date_list]

    target_moto=output_file.copy(deep=True)

    output_file["生産日"]= pd.to_datetime(output_file['生産日'],format='%Y-%m-%d')

    target_data=output_file[output_file["生産日"]>date_list]

    dat=target_data["生産日"].tolist()
    dates=[]
    for ele in dat:
        ele=pd.to_datetime(ele,format='%Y-%m-%d')
        if ele not in dates:
            dates.append(ele)
    

    # target_data=target_data[target_data["生産日"]<=date_list]

    target_data["納期"]=pd.to_datetime(target_data["納期"],format='%Y-%m-%d')

    target_data=func_get_all_variables(target_data)

    # print(target_data["納期_copy"])
    Class_Data=[]
 

    for ind,row in target_data.iterrows():
        class_data=Data_provider(row.品目コード,
                                row.品名,
                                row.ライン,
                                row.ライン名,
                                row.入目,
                                row.流速,
                                row.テンパリング,
                                row.沃素価,
                                row.KI製品,
                                row.初回限定,
                                row.最終限定,
                                row.リパック,
                                row.予定数量,
                                row.納期,
                                row.チケットNO,
                                row.備考,
                                row.生産日,
                                row.順番,
                                row.slot,
                                row.time_taken,
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
                                used=0,
                                cleaning_jikan=0)
        
        Class_Data.append(class_data)   

    
    
    Class_Data=Class_Data+unused_class_data+used_class_data
        


    Class_Data=sorted(Class_Data, key=lambda x: x.get_seisanbi(), reverse=False)

    flag_object=[]

    see_future=3
    for ele in dates:
        ibj1= Stretch_Flag_setter(ele,see_future)
        flag_object.append(ibj1)


    print(dates)
    final_df2=pd.DataFrame(columns=target_moto.columns)

    unused_df=pd.DataFrame(columns=target_moto.columns)
    final_df,Class_Data=schedule_manager(Class_Data,dates,final_df2,flag_object,see_future)
    # final_df,Class_Data=special_function(Class_Data,final_df2,flag_object,see_future,dates)

    output_file_backup = output_file_backup.append(final_df, ignore_index=True)

    output_file_backup=output_file_backup.sort_values(['生産日', '順番'], ascending=[True, True])

    # output_file_backup.sort_values(['生産日', ], ascending=[True])


    output_file_backup.to_csv("output2.csv",encoding="utf-8_sig",index=False)
    non_final_df,unused_class_data,used_class_data=unused_dataframe(Class_Data,unused_df)



non_final_df,unused_class_data,used_class_data=one_day_replanner()
remaining_planner(unused_class_data,used_class_data)

