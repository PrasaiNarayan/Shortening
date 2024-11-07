
import pandas as pd
from datetime import date, timedelta
import math
from Provider import Data_provider
import Record_finder
from Provider import Stretch_Flag_setter

from schedule_manage import stretch_allowable_two_args,check_allowable,fuction_to_allocate

def orig_Data_given_day(original_plan,ele):
    original_plan=original_plan[original_plan["生産日"]==ele]
    return original_plan


def special_function(Class_Data_moto,final_df2,flag_object,see_future,dates,speciial_records,current_date):
    # date_list=speciial_records['納期_copy'].tolist()[0]
    date_list=[current_date]
    for elements in date_list:
        
        elements=pd.to_datetime(elements)
        start_time=elements

        if elements.day_name()=='Sunday' or elements.day_name()=='Saturday':
            total_time=860
            cleaning_time=30
        else:
            total_time=900
            cleaning_time=20

        special_data_of_given_day=speciial_records[speciial_records["納期_copy"]==elements]


        Class_Data=[]
        for ind,row in special_data_of_given_day.iterrows():
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


        today_data=[]
        for ele in Class_Data:
            today_data.append(ele)
        future_data=Class_Data_moto
        future_with_today=Class_Data+future_data
        Class_Data=future_with_today

        print(len(future_with_today))

        if elements.day_name()=='Sunday' or elements.day_name()=='Saturday':
          
            cleaning_time=30
            total_time=860
        else:

            cleaning_time=20
            total_time=900

        today_first_records=[]
        today_last_records=[]
        
        today_first_records=Record_finder.first_record_finder(today_data,types='○')
        for ele in today_first_records:
            if ele==today_first_records[0]:
                ele.set_cleaning_time(60)
            else:
                ele.set_cleaning_time(0)
            # print(ele.get_cleaning_time())
        if len(today_first_records)==0:
            today_first_records=Record_finder.first_record_finder_three(today_data,types='MCｼｮｰﾄ')
            if len(today_first_records)>0:
                mc_record=Record_finder.first_record_finder_renzoku(today_data,type1='ｲﾄｳIK-NT(H)', type2='ﾊﾟﾈﾘ-PV(13)')
                for ele in mc_record:
                    today_first_records.append(ele)
        
        if len(today_first_records)==0:
            today_first_records=Record_finder.first_record_finder_two(today_data,types='初回限定')

        if len(today_first_records)==0:
            today_first_records=Record_finder.first_record_finder_two(today_data,types='副原料添加なし初回限定')
            rem_renzoku_record=Record_finder.first_record_finder_three(today_data,types='ﾌﾟﾚﾐｱﾑｼﾖ-ﾄ-CF(S)')
            for re in rem_renzoku_record:
                if re not in today_first_records:
                    today_first_records.append(re)

                
        total_time_for_today_first_record=0
        copy_records=today_first_records

        

        for record in copy_records:  
            total_time_for_today_first_record+=record.get_cleaning_time()+getattr(record,f'get_{line}_time_taken')()+cleaning_time



        today_last_records=Record_finder.last_record_finder(today_data,types='高沃素価')
        rem_jyunko_dekiru=Record_finder.last_record_finder(today_data,types='準高沃素価')

        for ele in rem_jyunko_dekiru:
            today_last_records.append(ele)

        if len(today_last_records)==0:
                today_last_records=Record_finder.last_record_finder(today_data,types='低沃素価')

        if len(today_last_records)==0:
            today_last_records=Record_finder.last_record_finder_two(today_data,types='B')
            rem_arerukon_records=Record_finder.last_record_finder_four_MOS(today_data,types='〇')

            arerukon_re=rem_arerukon_records
            nep=[]
            # shifting record with name ﾊｲDXﾌｱﾂﾄ(H) to last
            for tokui_rec in arerukon_re:
                if tokui_rec.get_syouhin_name()=='ﾊｲDXﾌｱﾂﾄ(H)':
                    nep.append(tokui_rec)
                    rem_arerukon_records.remove(tokui_rec)
            for ele in nep:
                rem_arerukon_records.append(ele)

            for ele in rem_arerukon_records:
                today_last_records.append(ele)

        if len(today_last_records)==0:
            today_last_records=Record_finder.last_record_finder_three(today_data,types='〇')
        
        
        copy_records=today_last_records
        # today_last_records=stretch_allowable(today_last_records,copy_records,flag_object,elements)

        total_time_for_today_last_records=0
        for record in today_last_records:      
            # before_time=final_time
            # final_time=final_time-timedelta(minutes=record.get_cleaning_time())-timedelta(minutes=getattr(record,f'get_{line}_time_taken')())
            total_time_for_today_last_records+=record.get_cleaning_time()+getattr(record,f'get_{line}_time_taken')()+cleaning_time




        #the data without first and last priority normal elements of the given day

        non_priority_record=[]

        # total_time_for_non_prior_records=0
        for non_prior in today_data:
            if non_prior.get_used()==0 and non_prior.get_firsts()==0 and non_prior.get_lasts()==0 and non_prior.get_last_first()==0:
               
                non_priority_record.append(non_prior)

        # non_priority_record=stretch_allowable(non_priority_record,non_priority_record,flag_object,elements)

        allowable_start_time=start_time+timedelta(minutes=440)
        # allowable_finish_time=start_time+timedelta(minutes=1380)

        all_records=[]

        if len(today_first_records)>0 and len(today_last_records)>0:
            print("both non zero")
            MC_short_check=False
            
            remaining_time=total_time-total_time_for_today_first_record-total_time_for_today_last_records

            non_prior_list=[]
            for ele in non_priority_record:
                if remaining_time-ele.get_cleaning_time()-getattr(ele,f'get_{line}_time_taken')()-cleaning_time>0:
                    if ele.get_weight_limit()==1:
                        bools,current_ele_set_end_time=check_allowable(remaining_time,elements,Class_Data,ele,line)
                        

                        if bools:
                            ele.set_end_time(current_ele_set_end_time)
                            ele.set_used(1)
                            non_prior_list.append(ele)
                            remaining_time=remaining_time-ele.get_cleaning_time()-getattr(ele,f'get_{line}_time_taken')()-cleaning_time
                       
                    else:
                        non_prior_list.append(ele)
                        remaining_time= remaining_time-ele.get_cleaning_time()-getattr(ele,f'get_{line}_time_taken')()-cleaning_time

            today_with_future_first_records=[]
            if today_first_records[0].get_KI()=='○':
                today_with_future_first_records=Record_finder.first_record_finder(future_with_today,types='○')

                for ele in today_with_future_first_records:
                    if ele==today_with_future_first_records[0]:
                        ele.set_cleaning_time(60)
                    else:
                        ele.set_cleaning_time(0)

            elif today_first_records[0].get_syouhin_name().startswith('MCｼｮｰﾄ'):
                today_with_future_first_records=Record_finder.first_record_finder_three(future_with_today,types='MCｼｮｰﾄ')
                mc_record=Record_finder.first_record_finder_renzoku(future_with_today,type1='ｲﾄｳIK-NT(H)', type2='ﾊﾟﾈﾘ-PV(13)')
                for ele in mc_record:
                    today_with_future_first_records.append(ele)

                MC_short_check=True

            elif today_first_records[0].get_bikou()=='初回限定':
                today_with_future_first_records=Record_finder.first_record_finder_two(future_with_today,types='初回限定')

            elif today_first_records[0].get_bikou()=='副原料添加なし初回限定' or today_first_records[0].get_syouhin_name()=='ﾌﾟﾚﾐｱﾑｼﾖ-ﾄ-CF(S)':
                today_with_future_first_records=Record_finder.first_record_finder_two(future_with_today,types='副原料添加なし初回限定')
                rem_renzoku_record=Record_finder.first_record_finder_three(future_with_today,types='ﾌﾟﾚﾐｱﾑｼﾖ-ﾄ-CF(S)')
                for re in rem_renzoku_record:
                    if re not in today_with_future_first_records:
                        today_with_future_first_records.append(re)

            
            # today_first_records.clear()

            for ele in today_with_future_first_records:
                if ele not in today_first_records:
                    if remaining_time-ele.get_cleaning_time()-getattr(ele,f'get_{line}_time_taken')()-cleaning_time>0:
                        today_first_records.append(ele)
                        remaining_time= remaining_time-ele.get_cleaning_time()-getattr(ele,f'get_{line}_time_taken')()-cleaning_time
                    else:
                        break
            
            today_first_records,remaining_time=stretch_allowable_two_args(today_first_records,today_first_records,flag_object,elements,remaining_time,dates)

            refrence_time=remaining_time
            length=len(today_first_records)
            if length>1:
                if today_first_records[0].get_KI()=='○':
                    today_first_records[0].set_cleaning_time(0)
                    today_first_records[-1].set_cleaning_time(60)

            
            today_with_future_last_records=[]
            if today_last_records[0].get_yousoka()=='高沃素価' or today_last_records[0].get_yousoka()=='準高沃素価':
                today_with_future_last_records=Record_finder.last_record_finder(future_with_today,types='高沃素価')
                jyunko_dekiru=Record_finder.last_record_finder(future_with_today,types='準高沃素価')

                for ele in jyunko_dekiru:
                    today_with_future_last_records.append(ele)

            elif today_last_records[0].get_yousoka()=='低沃素価':
                today_with_future_last_records=Record_finder.last_record_finder(future_with_today,types='低沃素価')
            

            elif today_last_records[0].get_Allergy()=='B' or today_last_records[0].get_MOS()=='〇':
                today_with_future_last_records=Record_finder.last_record_finder_two(future_with_today,types='B')
                arerukon_records=Record_finder.last_record_finder_four_MOS(future_with_today,types='〇')
                arerukon_re=arerukon_records
                nep=[]
                # shifting record with name ﾊｲDXﾌｱﾂﾄ(H) to last
                for tokui_rec in arerukon_re:
                    if tokui_rec.get_syouhin_name()=='ﾊｲDXﾌｱﾂﾄ(H)':
                        nep.append(tokui_rec)
                        arerukon_records.remove(tokui_rec)

                for ele in nep:
                    arerukon_records.append(ele)


                for ele in arerukon_records:
                    today_with_future_last_records.append(ele)

            elif today_last_records[0].get_saishu_gentei()=='〇':
                today_with_future_last_records=Record_finder.last_record_finder_three(future_with_today,types='〇')

            for ele in today_with_future_last_records:
                if ele not in today_last_records:
                    if remaining_time-ele.get_cleaning_time()-getattr(ele,f'get_{line}_time_taken')()-cleaning_time>0:
                        today_last_records.append(ele)
                        remaining_time= remaining_time-ele.get_cleaning_time()-getattr(ele,f'get_{line}_time_taken')()-cleaning_time


            today_last_records,remaining_time=stretch_allowable_two_args(today_last_records,today_last_records,flag_object,elements,remaining_time,dates)

            future_non_prior_list=[]
            # using tempahin data upto 7 days and other upto 3 days
            for ele in future_data:
                if ele.get_firsts()==0 and ele.get_lasts()==0 and ele.get_last_first()==0 and ele.get_used()==0 and ele.get_weight_limit()==1:
                    if remaining_time-ele.get_cleaning_time()-getattr(ele,f'get_{line}_time_taken')()-cleaning_time>0:
                        # if ele.get_weight_limit()==1:
                        bools,current_ele_set_end_time=check_allowable(refrence_time,elements,Class_Data,ele)
                        
                        if bools:
                            print(ele.get_syouhin_name())
                            ele.set_end_time(current_ele_set_end_time)
                            ele.set_used(1)
                            future_non_prior_list.append(ele)
                            remaining_time= remaining_time-ele.get_cleaning_time()-getattr(ele,f'get_{line}_time_taken')()-cleaning_time
                            refrence_time=refrence_time-ele.get_cleaning_time()-getattr(ele,f'get_{line}_time_taken')()-cleaning_time
                  

            future_non_prior_list,remaining_time=stretch_allowable_two_args(future_non_prior_list,future_non_prior_list,flag_object,elements,remaining_time,dates)

            # future_non_prior_list_with_no_weight_limit=[]
            future_non_prior_list1=[]
            for ele in future_data:
                if ele.get_firsts()==0 and ele.get_lasts()==0 and ele.get_last_first()==0 and ele.get_used()==0 and ele.get_weight_limit()==0:
                    if remaining_time-ele.get_cleaning_time()-getattr(ele,f'get_{line}_time_taken')()-cleaning_time>0:
                        future_non_prior_list1.append(ele)
                        remaining_time= remaining_time-ele.get_cleaning_time()-getattr(ele,f'get_{line}_time_taken')()-cleaning_time

            future_non_prior_list1,remaining_time=stretch_allowable_two_args(future_non_prior_list1,future_non_prior_list1,flag_object,elements,remaining_time,dates)

            future_non_prior_list=future_non_prior_list+future_non_prior_list1
            today_last_records.reverse() 

        # adding record with names 'ｲﾄｳIK-NT(H)' and 'ﾊﾟﾈﾘ-PV(13)' just after the record with name 'MCｼｮｰﾄ' 
            non_prior_list=fuction_to_allocate(remaining_time,future_with_today,non_prior_list,elements,Class_Data,flag_object,dates,future_with_today)
            
            today_last_records.reverse()

            non_pror=non_prior_list+future_non_prior_list
            if MC_short_check:
                OP=[]
                GP=non_pror
                for ele in GP:
                    if ele.get_syouhin_name()=='ｲﾄｳIK-NT(H)' or ele.get_syouhin_name()=='ﾊﾟﾈﾘ-PV(13)':
                        non_pror.remove(ele)
                        OP.append(ele)

                today_first_records=today_first_records+OP


            


            all_records=today_first_records+non_pror+today_last_records


        # first finding out whether last end records and first records are present or not
        # if they are empy then go for future records to find the probable first end and last end records
        
        elif len(today_first_records)==0 and len(today_last_records)==0:
            print('both zero')
            MC_short_check=False
            future_first_records=[]
            dummy=[]
            for ele in future_data:
                if ele.get_firsts()==1:
                    dummy.append(ele)

            top_rec=None
            if len(dummy)>0:
                top_rec=dummy[0]


            if top_rec!=None:
                
                if top_rec.get_KI()=='○':
                    future_first_records=Record_finder.first_record_finder(future_data,types='○')
                    # print(start_time)

                    for ele in future_first_records:
                        if ele==future_first_records[0]:
                            ele.set_cleaning_time(60)
                        else:
                            ele.set_cleaning_time(0)
                        # print(ele.get_cleaning_time())

                # get_syouhin_name()
                elif top_rec.get_syouhin_name().startswith('MCｼｮｰﾄ'):
                    future_first_records=Record_finder.first_record_finder_three(future_data,types='MCｼｮｰﾄ')

                    mc_record=Record_finder.first_record_finder_renzoku(future_data,type1='ｲﾄｳIK-NT(H)', type2='ﾊﾟﾈﾘ-PV(13)')
                    for ele in mc_record:
                        future_first_records.append(ele)

                    MC_short_check=True

                elif top_rec.get_bikou()=='初回限定':
                    future_first_records=Record_finder.first_record_finder_two(future_data,types='初回限定')

                elif top_rec.get_bikou()=='副原料添加なし初回限定' or top_rec.get_syouhin_name()=='ﾌﾟﾚﾐｱﾑｼﾖ-ﾄ-CF(S)':
                    future_first_records=Record_finder.first_record_finder_two(future_data,types='副原料添加なし初回限定')
                    rem_renzoku_record=Record_finder.first_record_finder_three(future_data,types='ﾌﾟﾚﾐｱﾑｼﾖ-ﾄ-CF(S)')
                    
                    for re in rem_renzoku_record:
                        if re not in future_first_records:
                            future_first_records.append(re)

            
            

            # print(f'the length of future_records :{future_data}')
            # for ele in future_data:
            #     print(ele.get_yousoka())
            dummy2=[]
            for ele in future_data:
                if ele.get_lasts()==1 or ele.get_last_first()==1:
                    dummy2.append(ele)

            top_rec2=None
            if len(dummy2)>0:
                top_rec2=dummy2[0]
            future_last_records=[]
            if top_rec2!=None:
                if top_rec2.get_yousoka()=='高沃素価' or top_rec2.get_yousoka()=='準高沃素価':
                    future_last_records=Record_finder.last_record_finder(future_data,types='高沃素価')
                    jyunko_dekiru=Record_finder.last_record_finder(future_data,types='準高沃素価')

                    for ele in jyunko_dekiru:
                        future_last_records.append(ele)

                elif top_rec2.get_yousoka()=='低沃素価':
                    future_last_records=Record_finder.last_record_finder(future_data,types='低沃素価')
            

                elif top_rec2.get_Allergy()=='B' or top_rec2.get_MOS()=='〇':
             
                    future_last_records=Record_finder.last_record_finder_two(future_data,types='B')
                    arerukon_records=Record_finder.last_record_finder_four_MOS(future_data,types='〇')

                    # for ele in arerukon_records:
                    #     if ele.get_weight_limit()==1:
                    #         check_allowable(refrence_time,elements,Class_Data,arerukon_records)

                    arerukon_re=arerukon_records
                    nep=[]
                    # shifting record with name ﾊｲDXﾌｱﾂﾄ(H) to last
                    for tokui_rec in arerukon_re:
                        if tokui_rec.get_syouhin_name()=='ﾊｲDXﾌｱﾂﾄ(H)':
                            nep.append(tokui_rec)
                            arerukon_records.remove(tokui_rec)
                    for ele in nep:
                        arerukon_records.append(ele)


                    for ele in arerukon_records:
                        future_last_records.append(ele)

                elif top_rec2.get_saishu_gentei()=='〇':
                    future_last_records=Record_finder.last_record_finder_three(future_data,types='〇')

            # print(f'the length of future_last_records :{future_last_records}')


            future_non_prior_records=[]
            for fut_rec in future_data:
                
                
                if fut_rec.get_used()==0 and fut_rec.get_firsts()==0 and fut_rec.get_lasts()==0 and fut_rec.get_last_first()==0:
                    future_non_prior_records.append(fut_rec)


            remaining_time=total_time#-total_time_for_non_prior_records
            # handeling non priority records
            non_prior_list=[]
            for ele in non_priority_record:
                if remaining_time-ele.get_cleaning_time()-getattr(ele,f'get_{line}_time_taken')()-cleaning_time>0:
                    if ele.get_weight_limit()==1:
                        
                        bools,current_ele_set_end_time=check_allowable(remaining_time,elements,Class_Data,ele,line)
                     
                  
                        if bools:
                            ele.set_end_time(current_ele_set_end_time)
                            ele.set_used(1)
                            non_prior_list.append(ele)
                            remaining_time=remaining_time-ele.get_cleaning_time()-getattr(ele,f'get_{line}_time_taken')()-cleaning_time

                    else:
                        non_prior_list.append(ele)
                        remaining_time=remaining_time-ele.get_cleaning_time()-getattr(ele,f'get_{line}_time_taken')()-cleaning_time


            non_prior_list,remaining_time=stretch_allowable_two_args(non_prior_list,non_prior_list,flag_object,elements,remaining_time,dates)

            today_usable_future_last_records=[]
            today_usable_future_first_records=[]


            for prior_recs in future_first_records:
                if remaining_time-prior_recs.get_cleaning_time()-prior_recs.get_time_taken()-cleaning_time>0:
                    today_usable_future_first_records.append(prior_recs)
                    remaining_time=remaining_time-prior_recs.get_cleaning_time()-prior_recs.get_time_taken()-cleaning_time
                else:
                    break
            length=len(today_usable_future_first_records)
            if length>1:
                if today_usable_future_first_records[0].get_KI()=='○':
                    # print(length)
                    today_usable_future_first_records[0].set_cleaning_time(0)
                    today_usable_future_first_records[-1].set_cleaning_time(60)

            # if length==1:
            #     if today_usable_future_first_records[0].get_KI()=='○':
            #         print(f"this is: {today_usable_future_first_records[0].get_cleaning_time()}")
            today_usable_future_first_records,remaining_time=stretch_allowable_two_args(today_usable_future_first_records,today_usable_future_first_records,flag_object,elements,remaining_time,dates)

            refrence_time=remaining_time

            for prior_recs in future_last_records:
                if remaining_time-prior_recs.get_cleaning_time()-prior_recs.get_time_taken()-cleaning_time>0:
                    if prior_recs.get_weight_limit()==1:
                        bools,current_ele_set_end_time=check_allowable(remaining_time,elements,Class_Data,prior_recs)
                        if bools:
                            prior_recs.set_end_time(current_ele_set_end_time)
                            prior_recs.set_used(1)
                            today_usable_future_last_records.append(prior_recs)
                            remaining_time=remaining_time-prior_recs.get_cleaning_time()-prior_recs.get_time_taken()-cleaning_time

                    else:
                        today_usable_future_last_records.append(prior_recs)
                        remaining_time=remaining_time-prior_recs.get_cleaning_time()-prior_recs.get_time_taken()-cleaning_time

            today_usable_future_last_records,remaining_time=stretch_allowable_two_args(today_usable_future_last_records,today_usable_future_last_records,flag_object,elements,remaining_time,dates)
            # print(remaining_time)
            # for non_prior_recs in future_non_prior_records:
            non_prior_list1=[]
            for non_prior_recs in future_data:
                if remaining_time-non_prior_recs.get_cleaning_time()-non_prior_recs.get_time_taken()-cleaning_time>0:
                    if non_prior_recs.get_weight_limit()==1 and non_prior_recs.get_used()==0 and non_prior_recs.get_firsts()==0 and non_prior_recs.get_lasts()==0 and non_prior_recs.get_last_first()==0:

                        bools,current_ele_set_end_time=check_allowable(remaining_time,elements,Class_Data,non_prior_recs)

                        if bools:
                            
                            non_prior_recs.set_end_time(current_ele_set_end_time)
                            non_prior_recs.set_used(1)
                            non_prior_list1.append(non_prior_recs)
                            remaining_time=remaining_time-non_prior_recs.get_cleaning_time()-non_prior_recs.get_time_taken()-cleaning_time
                            refrence_time=refrence_time-non_prior_recs.get_cleaning_time()-non_prior_recs.get_time_taken()-cleaning_time


            non_prior_list1,remaining_time=stretch_allowable_two_args(non_prior_list1,non_prior_list1,flag_object,elements,remaining_time,dates)
            # print(f"Fut non pror recs {len(future_non_prior_records)}")
            non_prior_list2=[]
            for non_prior_recs in future_non_prior_records:
                # print(non_prior_recs.get_syouhin_name())
                if remaining_time-non_prior_recs.get_cleaning_time()-non_prior_recs.get_time_taken()-cleaning_time>0:
                    if non_prior_recs.get_weight_limit()==0:
                        non_prior_list2.append(non_prior_recs)
                        remaining_time=remaining_time-non_prior_recs.get_cleaning_time()-non_prior_recs.get_time_taken()-cleaning_time
                        # print(remaining_time)

            non_prior_list2,remaining_time=stretch_allowable_two_args(non_prior_list2,non_prior_list2,flag_object,elements,remaining_time,dates)
            # if still time is remaining and but tempahin has not been able to be alocated then 
            # shifting time and making sure the remaining tempahin will be allocated
            non_prior_list=non_prior_list+non_prior_list1+non_prior_list2

            non_prior_list=fuction_to_allocate(remaining_time,future_with_today,non_prior_list,elements,Class_Data,flag_object,dates,future_with_today)
            
            today_usable_future_last_records.reverse()

            # print(f'today_usable future_first_records :{today_usable_future_first_records}')

            non_pror=non_prior_list
            if MC_short_check:
                OP=[]
                GP=non_pror
                for ele in GP:
                    if ele.get_syouhin_name()=='ｲﾄｳIK-NT(H)' or ele.get_syouhin_name()=='ﾊﾟﾈﾘ-PV(13)':
                        non_pror.remove(ele)
                        OP.append(ele)

                today_usable_future_first_records=today_usable_future_first_records+OP


            all_records=today_usable_future_first_records+non_pror+today_usable_future_last_records
            # print(all_records)

            # for ele in all_records:
            #     print(ele.get_KI())


        elif len(today_first_records)==0 and len(today_last_records)!=0:
            print("first Zero last non Zero")
            for ele in Class_Data:
                print(f"{ele.get_syouhin_name()},{ele.get_used()}")

            MC_short_check=False
            remaining_time=total_time#-total_time_for_today_last_records

            today_non_prior_list=[]
            for ele in non_priority_record:
                if remaining_time-ele.get_cleaning_time()-getattr(ele,f'get_{line}_time_taken')()-cleaning_time>0:

                    if ele.get_weight_limit()==1:
                        bools,current_ele_set_end_time=check_allowable(remaining_time,elements,Class_Data,ele,line)
                        if bools:
                            ele.set_end_time(current_ele_set_end_time)
                            ele.set_used(1)
                            today_non_prior_list.append(ele)
                            remaining_time=remaining_time-ele.get_cleaning_time()-getattr(ele,f'get_{line}_time_taken')()-cleaning_time

                    else:
                        today_non_prior_list.append(ele)
                        remaining_time=remaining_time-ele.get_cleaning_time()-getattr(ele,f'get_{line}_time_taken')()-cleaning_time


            today_non_prior_list,remaining_time=stretch_allowable_two_args(today_non_prior_list,today_non_prior_list,flag_object,elements,remaining_time,dates)


            # future_last_record_lists_along_with_today

            today_with_future_last_records=[]
            if today_last_records[0].get_yousoka()=='高沃素価' or today_last_records[0].get_yousoka()=='準高沃素価':
                today_with_future_last_records=Record_finder.last_record_finder(future_with_today,types='高沃素価')
                jyunko_dekiru=Record_finder.last_record_finder(future_with_today,types='準高沃素価')

                for ele in jyunko_dekiru:
                    print(ele.get_yousoka())
                    today_with_future_last_records.append(ele)

            elif today_last_records[0].get_yousoka()=='低沃素価':
                today_with_future_last_records=Record_finder.last_record_finder(future_with_today,types='低沃素価')
            

            elif today_last_records[0].get_Allergy()=='B' or today_last_records[0].get_MOS()=='〇':
                today_with_future_last_records=Record_finder.last_record_finder_two(future_with_today,types='B')
                arerukon_records=Record_finder.last_record_finder_four_MOS(future_with_today,types='〇')
                arerukon_re=arerukon_records
                nep=[]
                # shifting record with name ﾊｲDXﾌｱﾂﾄ(H) to last
                for tokui_rec in arerukon_re:
                    if tokui_rec.get_syouhin_name()=='ﾊｲDXﾌｱﾂﾄ(H)':
                        nep.append(tokui_rec)
                        arerukon_records.remove(tokui_rec)
                for ele in nep:
                    arerukon_records.append(ele)

                for ele in arerukon_records:
                    today_with_future_last_records.append(ele)

            elif today_last_records[0].get_saishu_gentei()=='〇':
                today_with_future_last_records=Record_finder.last_record_finder_three(future_with_today,types='〇')


            today_last_records.clear()
            for ele in today_with_future_last_records:
                if ele not in today_last_records:
                    if remaining_time-ele.get_cleaning_time()-getattr(ele,f'get_{line}_time_taken')()-cleaning_time>0:
                        today_last_records.append(ele)
                        remaining_time= remaining_time-ele.get_cleaning_time()-getattr(ele,f'get_{line}_time_taken')()-cleaning_time



            today_last_records,remaining_time=stretch_allowable_two_args(today_last_records,today_last_records,flag_object,elements,remaining_time,dates)
            # getting future non prior lists
            print(remaining_time)


            future_first_records=[]
            dummy=[]
            for ele in future_data:
                if ele.get_firsts()==1:
                    dummy.append(ele)

            top_rec=None
            if len(dummy)>0:
                top_rec=dummy[0]


            if top_rec!=None:
                if top_rec.get_KI()=='○':
                    future_first_records=Record_finder.first_record_finder(future_data,types='○')
                    for ele in future_first_records:
                        if ele==future_first_records[0]:
                            ele.set_cleaning_time(60)
                        else:
                            ele.set_cleaning_time(0)
                        # print(ele.get_cleaning_time())

                # get_syouhin_name()
                elif top_rec.get_syouhin_name().startswith('MCｼｮｰﾄ'):
                    future_first_records=Record_finder.first_record_finder_three(future_data,types='MCｼｮｰﾄ')
                    mc_record=Record_finder.first_record_finder_renzoku(future_data,type1='ｲﾄｳIK-NT(H)', type2='ﾊﾟﾈﾘ-PV(13)')
                    for ele in mc_record:
                        future_first_records.append(ele)
                    MC_short_check=True

                elif top_rec.get_bikou()=='初回限定':
                    future_first_records=Record_finder.first_record_finder_two(future_data,types='初回限定')

                elif top_rec.get_bikou()=='副原料添加なし初回限定' or top_rec.get_syouhin_name()=='ﾌﾟﾚﾐｱﾑｼﾖ-ﾄ-CF(S)':
                    future_first_records=Record_finder.first_record_finder_two(future_data,types='副原料添加なし初回限定')
                    rem_renzoku_record=Record_finder.first_record_finder_three(future_data,types='ﾌﾟﾚﾐｱﾑｼﾖ-ﾄ-CF(S)')
                    for re in rem_renzoku_record:
                        if re not in future_first_records:
                            future_first_records.append(re)



            future_first_records_list=[]
            
            for ele in future_first_records:
                if remaining_time-ele.get_cleaning_time()-getattr(ele,f'get_{line}_time_taken')()-cleaning_time>0:
                    future_first_records_list.append(ele)
                    remaining_time=remaining_time-ele.get_cleaning_time()-getattr(ele,f'get_{line}_time_taken')()-cleaning_time
                    
                else:
                    break

            length=len(future_first_records_list)
            if length>1:
                if future_first_records_list[0].get_KI()=='○':
                    future_first_records_list[0].set_cleaning_time(0)
                    future_first_records_list[-1].set_cleaning_time(60)


            future_first_records_list,remaining_time=stretch_allowable_two_args(future_first_records_list,future_first_records_list,flag_object,elements,remaining_time,dates)

            # interpretation of the time for non prior records 

                    
            refrence_time=remaining_time


            future_non_prior_records=[]

            for fut_rec in future_data:
                if fut_rec.get_used()==0 and fut_rec.get_firsts()==0 and fut_rec.get_lasts()==0 and fut_rec.get_last_first()==0:
                    future_non_prior_records.append(fut_rec)


            future_non_prior_list=[]
            for ele in future_data:
                if remaining_time-ele.get_cleaning_time()-getattr(ele,f'get_{line}_time_taken')()-cleaning_time>0:
                    if ele.get_weight_limit()==1 and ele.get_used()==0 and ele.get_firsts()==0 and ele.get_lasts()==0 and ele.get_last_first()==0:
                     
                        #
                        bools,current_ele_set_end_time=check_allowable(refrence_time,elements,Class_Data,ele)
                        if bools:
                            ele.set_end_time(current_ele_set_end_time)
                            ele.set_used(1)
                            future_non_prior_list.append(ele)
                            remaining_time=remaining_time-ele.get_cleaning_time()-getattr(ele,f'get_{line}_time_taken')()-cleaning_time
                            refrence_time=refrence_time-ele.get_cleaning_time()-getattr(ele,f'get_{line}_time_taken')()-cleaning_time

                    
                    # else:
                    #     future_non_prior_list.append(ele)
                    #     remaining_time=remaining_time-ele.get_cleaning_time()-getattr(ele,f'get_{line}_time_taken')()-cleaning_time

            future_non_prior_list,remaining_time=stretch_allowable_two_args(future_non_prior_list,future_non_prior_list,flag_object,elements,remaining_time,dates)
            print(remaining_time)

            future_non_prior_list1=[]
            for ele in future_non_prior_records:
                if remaining_time-ele.get_cleaning_time()-getattr(ele,f'get_{line}_time_taken')()-cleaning_time>0:
                    if ele.get_weight_limit()==0:
                        future_non_prior_list1.append(ele)
                        remaining_time=remaining_time-ele.get_cleaning_time()-getattr(ele,f'get_{line}_time_taken')()-cleaning_time


            future_non_prior_list1,remaining_time=stretch_allowable_two_args(future_non_prior_list1,future_non_prior_list1,flag_object,elements,remaining_time,dates)
            
            print(remaining_time)
            future_non_prior_list=future_non_prior_list+future_non_prior_list1
            today_last_records.reverse()
            today_non_prior_list=fuction_to_allocate(remaining_time,future_with_today,today_non_prior_list,elements,Class_Data,flag_object,dates,future_with_today)

            non_pror=today_non_prior_list+future_non_prior_list
            if MC_short_check:
                OP=[]
                GP=non_pror
                for ele in GP:
                    if ele.get_syouhin_name()=='ｲﾄｳIK-NT(H)' or ele.get_syouhin_name()=='ﾊﾟﾈﾘ-PV(13)':
                        non_pror.remove(ele)
                        OP.append(ele)

                future_first_records_list=future_first_records_list+OP



            all_records=future_first_records_list+non_pror+today_last_records

            print(len(all_records))


            
                
        elif len(today_first_records)!=0 and len(today_last_records)==0:

            print("First non zero last zero")
            MC_short_check=False

            remaining_time=total_time#-total_time_for_today_first_record
            # refrence_time=remaining_time

            today_non_prior_list=[]
            for ele in non_priority_record:
                if remaining_time-ele.get_cleaning_time()-getattr(ele,f'get_{line}_time_taken')()-cleaning_time>0:
                    if ele.get_weight_limit()==1:
                        bools,current_ele_set_end_time=check_allowable(remaining_time,elements,Class_Data,ele,line)

                        if bools:
                            ele.set_end_time(current_ele_set_end_time)
                            ele.set_used(1)
                            today_non_prior_list.append(ele)
                            remaining_time=remaining_time-ele.get_cleaning_time()-getattr(ele,f'get_{line}_time_taken')()-cleaning_time
        
                    else:

                        today_non_prior_list.append(ele)
                        remaining_time=remaining_time-ele.get_cleaning_time()-getattr(ele,f'get_{line}_time_taken')()-cleaning_time


            today_non_prior_list,remaining_time=stretch_allowable_two_args(today_non_prior_list,today_non_prior_list,flag_object,elements,remaining_time,dates)

            today_with_future_first_records=[]
            
            if today_first_records[0].get_KI()=='○':
                today_with_future_first_records=Record_finder.first_record_finder(future_with_today,types='○')

                for ele in today_with_future_first_records:
                    if ele==today_with_future_first_records[0]:
                        ele.set_cleaning_time(60)
                        
                    else:
                        ele.set_cleaning_time(0)

                   
                # get_syouhin_name()
            elif today_first_records[0].get_syouhin_name().startswith('MCｼｮｰﾄ'):

                today_with_future_first_records=Record_finder.first_record_finder_three(future_with_today,types='MCｼｮｰﾄ')
                mc_record=Record_finder.first_record_finder_renzoku(future_with_today,type1='ｲﾄｳIK-NT(H)', type2='ﾊﾟﾈﾘ-PV(13)')
                for ele in mc_record:
                    today_with_future_first_records.append(ele)
                MC_short_check=True

            elif today_first_records[0].get_bikou()=='初回限定':
                today_with_future_first_records=Record_finder.first_record_finder_two(future_with_today,types='初回限定')

            elif today_first_records[0].get_bikou()=='副原料添加なし初回限定' or today_first_records[0].get_syouhin_name()=='ﾌﾟﾚﾐｱﾑｼﾖ-ﾄ-CF(S)':
                today_with_future_first_records=Record_finder.first_record_finder_two(future_with_today,types='副原料添加なし初回限定')
                rem_renzoku_record=Record_finder.first_record_finder_three(future_with_today,types='ﾌﾟﾚﾐｱﾑｼﾖ-ﾄ-CF(S)')
                for re in rem_renzoku_record:
                    if re not in today_with_future_first_records:
                        today_with_future_first_records.append(re)
                

            today_first_records.clear()
            for ele in today_with_future_first_records:
                if ele not in today_first_records:
                    if remaining_time-ele.get_cleaning_time()-getattr(ele,f'get_{line}_time_taken')()-cleaning_time>0:
                        today_first_records.append(ele)
                        remaining_time= remaining_time-ele.get_cleaning_time()-getattr(ele,f'get_{line}_time_taken')()-cleaning_time

                    else:
                        break

            length=len(today_with_future_first_records)
            if length>1:
                if today_with_future_first_records[0].get_KI()=='○':
                    today_with_future_first_records[0].set_cleaning_time(0)
                    today_with_future_first_records[-1].set_cleaning_time(60)

            today_first_records,remaining_time=stretch_allowable_two_args(today_first_records,today_first_records,flag_object,elements,remaining_time,dates)
            refrence_time=remaining_time

            dummy2=[]
            for ele in future_data:
                if ele.get_lasts()==1 or ele.get_last_first()==1:
                    dummy2.append(ele)

            top_rec2=None
            if len(dummy2)>0:
                top_rec2=dummy2[0]
            future_last_records=[]
            if top_rec2!=None:
                if top_rec2.get_yousoka()=='高沃素価' or top_rec2.get_yousoka()=='準高沃素価':
                    future_last_records=Record_finder.last_record_finder(future_data,types='高沃素価')
                    jyunko_dekiru=Record_finder.last_record_finder(future_data,types='準高沃素価')

                    for ele in jyunko_dekiru:
                        future_last_records.append(ele)

                elif top_rec2.get_yousoka()=='低沃素価':
                    future_last_records=Record_finder.last_record_finder(future_data,types='低沃素価')
            

                elif top_rec2.get_Allergy()=='B' or top_rec2.get_MOS()=='〇':
                    future_last_records=Record_finder.last_record_finder_two(future_data,types='B')
                    arerukon_records=Record_finder.last_record_finder_four_MOS(future_data,types='〇')
                    
                    arerukon_re=arerukon_records
                    nep=[]
                    # shifting record with name ﾊｲDXﾌｱﾂﾄ(H) to last
                    for tokui_rec in arerukon_re:
                        if tokui_rec.get_syouhin_name()=='ﾊｲDXﾌｱﾂﾄ(H)':
                            nep.append(tokui_rec)
                            arerukon_records.remove(tokui_rec)
                    for ele in nep:
                        arerukon_records.append(ele)


                    for ele in arerukon_records:
                        future_last_records.append(ele)

                elif top_rec2.get_saishu_gentei()=='〇':
                    future_last_records=Record_finder.last_record_finder_three(future_data,types='〇')

            
            future_last_records_list=[]

            for ele in future_last_records:
                if remaining_time-ele.get_cleaning_time()-getattr(ele,f'get_{line}_time_taken')()-cleaning_time>0:
                    future_last_records_list.append(ele)
                    remaining_time=remaining_time-ele.get_cleaning_time()-getattr(ele,f'get_{line}_time_taken')()-cleaning_time


            future_last_records_list,remaining_time=stretch_allowable_two_args(future_last_records_list,future_last_records_list,flag_object,elements,remaining_time,dates)
            # getting future non prior lists
            future_non_prior_records=[]

            for fut_rec in future_data:
                if fut_rec.get_used()==0 and fut_rec.get_firsts()==0 and fut_rec.get_lasts()==0 and fut_rec.get_last_first()==0:
                    future_non_prior_records.append(fut_rec)

            future_non_prior_list=[]
            for ele in future_data:
                if remaining_time-ele.get_cleaning_time()-getattr(ele,f'get_{line}_time_taken')()-cleaning_time>0:
                    if ele.get_weight_limit()==1 and ele.get_used()==0 and ele.get_firsts()==0 and ele.get_lasts()==0 and ele.get_last_first()==0:

                    
                        bools,current_ele_set_end_time=check_allowable(refrence_time,elements,Class_Data,ele)
                        # print("IN")
                        if bools:
                            ele.set_end_time(current_ele_set_end_time)
                            ele.set_used(1)
                            future_non_prior_list.append(ele)
                            remaining_time=remaining_time-ele.get_cleaning_time()-getattr(ele,f'get_{line}_time_taken')()-cleaning_time
                            refrence_time=refrence_time-ele.get_cleaning_time()-getattr(ele,f'get_{line}_time_taken')()-cleaning_time
                      
                    # else:
                    #     future_non_prior_list.append(ele)
                    #     remaining_time=remaining_time-ele.get_cleaning_time()-getattr(ele,f'get_{line}_time_taken')()-cleaning_time

            future_non_prior_list,remaining_time=stretch_allowable_two_args(future_non_prior_list,future_non_prior_list,flag_object,elements,remaining_time,dates)
            future_non_prior_list1=[]
            for ele in future_non_prior_records:
                if remaining_time-ele.get_cleaning_time()-getattr(ele,f'get_{line}_time_taken')()-cleaning_time>0:
                    if ele.get_weight_limit()==0:
                        future_non_prior_list1.append(ele)
                        remaining_time=remaining_time-ele.get_cleaning_time()-getattr(ele,f'get_{line}_time_taken')()-cleaning_time

            future_non_prior_list1,remaining_time=stretch_allowable_two_args(future_non_prior_list1,future_non_prior_list1,flag_object,elements,remaining_time,dates)
            future_non_prior_list=future_non_prior_list+future_non_prior_list1
            future_last_records_list.reverse()
            today_non_prior_list=fuction_to_allocate(remaining_time,future_with_today,today_non_prior_list,elements,Class_Data,flag_object,dates,future_with_today)

            non_pror=today_non_prior_list+future_non_prior_list
            if MC_short_check:
                OP=[]
                GP=non_pror
                for ele in GP:
                    if ele.get_syouhin_name()=='ｲﾄｳIK-NT(H)' or ele.get_syouhin_name()=='ﾊﾟﾈﾘ-PV(13)':
                        non_pror.remove(ele)
                        OP.append(ele)

                today_first_records=today_first_records+OP


            all_records=today_first_records+non_pror+future_last_records_list

        task_wise_icrement=0

        # all_records=list(set(all_records))
        i=0
        prev_record=None
        
        for record in all_records:
            

            if i==0:
                before_time=allowable_start_time
            else:
                before_time=allowable_start_time+timedelta(minutes=cleaning_time)+timedelta(minutes=prev_record.get_cleaning_time())

            # if record.get_st_time()!=None:
            #     before_time=record.get_st_time()

            if (elements.day_name()=='Sunday' or elements.day_name()=='Saturday') and (saturday_special_time1-timedelta(minutes=cleaning_time)<=elements+timedelta(hours=17) and saturday_special_time2>elements+timedelta(hours=17)):
                before_time=before_time+timedelta(minutes=20)

            if (elements.day_name()=='Sunday' or elements.day_name()=='Saturday') and (saturday_special_time1-timedelta(minutes=cleaning_time)<=elements+timedelta(hours=11) and saturday_special_time2>elements+timedelta(hours=11)):
                before_time=before_time+timedelta(minutes=20)
               
            
            allowable_start_time=before_time+timedelta(minutes=getattr(record,f'get_{line}_time_taken')())
            record.set_slot(before_time,allowable_start_time)
            task_wise_icrement+=1
            record.set_jyounban(task_wise_icrement)

            record.set_seisanbi(start_time)
            record.set_used(1)
            record.set_end_time(allowable_start_time)


            prev_record=record

            saturday_special_time1=before_time
            saturday_special_time2=allowable_start_time

           
            i+=1

        # prev_Date=elements

        
        for ele in all_records:
            final_df2=final_df2.append({'品目コード':ele.get_syouhin_code(),
                                '品名':ele.get_syouhin_name(),
                                'ライン':ele.get_line(),
                                'ライン名':ele.get_line_name(),
                                '入目':ele.get_iri_me(),
                                '流速':ele.get_ryousoku(),
                                'テンパリング':ele.get_tenpahin(),
                                '沃素価':ele.get_yousoka(),
                                'KI':ele.get_KI(),
                                '初回限定':ele.get_syoukai_gentei(),
                                '最終限定':ele.get_saishu_gentei(),
                                'リパック':ele.get_stretch(),
                                '予定数量':ele.get_yotei_syourou(),
                                '納期':ele.get_nouki().date(),
                                'チケットNO':ele.get_ticket_no(),
                                '備考':ele.get_bikou(),
                                '生産日':ele.get_seisanbi(),
                                '順番':ele.get_jyounban(),
                                'slot':ele.get_slot(),
                                'nouki_copy':ele.get_nouki_copy().date()

            },
            ignore_index=True)

   

    return final_df2,future_with_today


def unused_dataframe(Class_Data,non_final_df):
    non_final_df["nouki_copy"]=None
    unused_class_data=[]
    used_class_data=[]
    for ele in Class_Data:
        # print(ele.get_used())
        if ele.get_used()==0:
            # unused_object_lists.append(ele)

            non_final_df=non_final_df.append({'品目コード':ele.get_syouhin_code(),
                                            '品名':ele.get_syouhin_name(),
                                            'ライン':ele.get_line(),
                                            'ライン名':ele.get_line_name(),
                                            '入目':ele.get_iri_me(),
                                            '流速':ele.get_ryousoku(),
                                            'テンパリング':ele.get_tenpahin(),
                                            '沃素価':ele.get_yousoka(),
                                            'KI':ele.get_KI(),
                                            '初回限定':ele.get_syoukai_gentei(),
                                            '最終限定':ele.get_saishu_gentei(),
                                            'リパック':ele.get_stretch(),
                                            '予定数量':ele.get_yotei_syourou(),
                                            '納期':ele.get_nouki(),
                                            'チケットNO':ele.get_ticket_no(),
                                            '備考':ele.get_bikou(),
                                            '生産日':ele.get_seisanbi(),
                                            '順番':ele.get_jyounban(),
                                            'slot':ele.get_slot(),
                                            'nouki_copy':ele.get_nouki_copy()
                                            },
                                            ignore_index=True)
            
            unused_class_data.append(ele)


        else:
            used_class_data.append(ele)


    non_final_df.to_csv(f"remaining_replanning_day.csv",encoding="utf-8_sig",index=False)

    return non_final_df,unused_class_data,used_class_data
    # return non_final_df


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


def one_day_replanner():
    speciial_records=pd.read_csv("select_data.csv",encoding="utf-8_sig")
    speciial_records['納期'] = pd.to_datetime(speciial_records['納期'],format='%Y%m%d')  
    speciial_records= func_get_all_variables(speciial_records)
    

    output_file=pd.read_csv("output.csv",encoding="utf-8_sig")
    output_file["生産日"]=pd.to_datetime(output_file["生産日"],format='%Y-%m-%d')
    output_file_backup=output_file

    speciial_records['納期_copy']=pd.to_datetime(speciial_records['納期_copy'],format='%Y%m%d')

    date_list2=speciial_records['納期_copy'].tolist()
    date_list1=[]

    for ele in date_list2:
        if ele not in date_list1:
            date_list1.append(ele)

    # date_list1=[ele for ele in date_list2 if ele not in date_list1 ]

  
    unused_df=pd.DataFrame(columns=output_file.columns)

    Big_Class=[]

    for date_list in date_list1:
        print(f"list of dates: {date_list}")
    

        # new_date_list=date_list.date()
        # print(new_date_list)
        output_file_backup=output_file_backup[output_file_backup["生産日"]!=date_list]

        target_moto=output_file.copy(deep=True)

        # output_file["生産日"]= pd.to_datetime(output_file['生産日'],format='%Y-%m-%d')

        target_data=output_file[output_file["生産日"]>=date_list-timedelta(days=1)]

        target_data=target_data[target_data["生産日"]<=date_list]

        target_data["納期"]=pd.to_datetime(target_data["納期"],format='%Y-%m-%d')

        target_data=func_get_all_variables(target_data)

        # print(target_data["納期_copy"])
        Class_Data=[]
        Class_Data1=[]
        Class_Data2=[]

        for ind,row in target_data.iterrows():
            if row.生産日==date_list:
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
                    
                Class_Data1.append(class_data)
            else:
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
                                        used=1,
                                        cleaning_jikan=0)
                    
                Class_Data2.append(class_data)

            




        Class_Data=Class_Data1+Class_Data2

        for ele in Class_Data:
            slot=ele.get_slot()
            if ele.get_used()==1:
                slot_second_part=slot.split("-->")[-1]
                slot_second_part=pd.to_datetime(slot_second_part)
                ele.set_end_time(slot_second_part)

        # for  ele in Class_Data:
        #     if ele.get_used()==1 and ele.get_weight_limit()==1:
        #         print(ele.get_end_time())



        flag_object=[]

        dates=[date_list-timedelta(days=1),date_list]
        see_future=3
        for ele in dates:
            ibj1= Stretch_Flag_setter(ele,see_future)
            flag_object.append(ibj1)

        # print(dates)

   
        final_df2=pd.DataFrame(columns=target_moto.columns)

        
        final_df,Class_Data=special_function(Class_Data,final_df2,flag_object,see_future,dates,speciial_records,date_list)

        output_file_backup = output_file_backup.append(final_df, ignore_index=True)

        output_file_backup=output_file_backup.sort_values(['生産日', '順番'], ascending=[True, True])

        # output_file_backup.sort_values(['生産日', ], ascending=[True])
        Big_Class=Big_Class+Class_Data


    output_file_backup.to_csv("output1.csv",encoding="utf-8_sig",index=False)
    non_final_df,unused_class_data,used_class_data=unused_dataframe(Big_Class,unused_df)

    return non_final_df,unused_class_data,used_class_data



# non_final_df,unused_class_data,used_class_data=one_day_replanner()