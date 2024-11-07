def record_finder_generic(data_list, types, attribute_check_func, indicator_check_func, set_used=False):
    data = []
    count_for_sequential = 0
    next_renzoku = True

    for obj in data_list:
        if indicator_check_func(obj) and attribute_check_func(obj, types) and obj.get_used() == 0:
            data.append(obj)
            if obj.get_clean_time() == 1:
                obj.set_cleaning_time(60)

            # If not more than one type of the same type is allowed
            if obj.get_no_renzoku_seisan() == 1:
                if not next_renzoku:
                    if obj in data:
                        data.remove(obj)
                else:
                    next_renzoku = False

            # If only a batch of two is allowed but not more than that
            if obj.get_only_two() == 1:
                count_for_sequential += 1
                if count_for_sequential > 2:
                    if obj in data:
                        data.remove(obj)

    records = []
    for ele in data:
        if ele not in records:
            records.append(ele)
            if set_used:
                ele.set_used(1)

    return records

# Attribute check functions
def attribute_check_get_KI(obj, types):
    return obj.get_KI() == types

def attribute_check_get_bikou(obj, types):
    # Check if the result of get_bikou() is not a float (which might indicate NaN)
    bikou_value = obj.get_bikou()

    if bikou_value is not None and not isinstance(bikou_value, float):
        if bikou_value.startswith(types):
            return obj.get_bikou().startswith(types)
        return False
    return False


def attribute_check_get_allergy(obj,types):
    return obj.get_Allergy()==types

def attribute_check_get_MOS(obj, types):
    return obj.get_MOS() == types

def attribute_check_syouhin_name_startswith(obj, types):
    return obj.get_syouhin_name().startswith(types)

def attribute_check_get_syoukai_gentei(obj, types):
    return obj.get_syoukai_gentei() == types

def attribute_check_syouhin_name_in(obj, types):
    return obj.get_syouhin_name() in types

def attribute_check_get_yousoka(obj, types):
    return obj.get_yousoka() == types

def attribute_check_get_saishu_gentei(obj, types):
    return obj.get_saishu_gentei() == types

# Indicator functions
def firsts_indicator(obj):
    return obj.get_firsts() == 1

def lasts_indicator(obj):
    return obj.get_lasts() == 1 or obj.get_last_first() == 1

def always_true(obj):
    return True

# Now, you can replace all the specific functions with calls to the generic function:
# For first_record_finder
def first_record_finder(today_data, types):
    return record_finder_generic(today_data, types, attribute_check_get_KI, firsts_indicator)

# For first_record_finder_two
def first_record_finder_two(today_data, types):
    return record_finder_generic(today_data, types, attribute_check_get_bikou, firsts_indicator)

# For first_record_finder_three
def first_record_finder_three(today_data, types):
    return record_finder_generic(today_data, types, attribute_check_syouhin_name_startswith, firsts_indicator)

# For first_record_finder_four
def first_record_finder_four(today_data, types):
    return record_finder_generic(today_data, types, attribute_check_get_syoukai_gentei, firsts_indicator)

# For first_record_finder_renzoku
def first_record_finder_renzoku(today_data, type1, type2):
    return record_finder_generic(today_data, [type1, type2], attribute_check_syouhin_name_in, always_true, set_used=True)

# For last_record_finder
def last_record_finder(remain_rec, types):
    return record_finder_generic(remain_rec, types, attribute_check_get_yousoka, lasts_indicator)

# For last_record_finder_two
def last_record_finder_two(remain_rec, types):
    return record_finder_generic(remain_rec, types, attribute_check_get_allergy, lasts_indicator)

def last_record_finder_four_MOS(remain_rec, types):
    return record_finder_generic(remain_rec, types, attribute_check_get_MOS, lasts_indicator)

# For last_record_finder_three
def last_record_finder_three(remain_rec, types):
    return record_finder_generic(remain_rec, types, attribute_check_get_saishu_gentei, lasts_indicator)




# def first_record_finder_renzoku(today_data,type1,type2):
#     first_data=[]          
#     next_renzoku=True
    
#     today_records=[]
#     next_renzoku=True
#     for objects in today_data:

#         if objects.get_used()==0:
#             if objects.get_syouhin_name()==type1 or objects.get_syouhin_name()==type2:
#             # and objects.get_clean_time()==1 and objects.get_no_renzoku_seisan()==1  and objects.get_weight_limit()==1 and objects.get_only_two()==1:
#                 first_data.append(objects)
#                 if objects.get_clean_time()==1:
#                     objects.set_cleaning_time(60)
                
#                 # if not more than one type of same tye is allowed
#                 if objects.get_no_renzoku_seisan()==1 :
#                     if next_renzoku==False:
#                         if objects in first_data:
#                             first_data.remove(objects)      
#                             # next_renzoku=False
#                     else:
#                         # first_data_clean_time_renzoku_seisan.append(objects)
#                         next_renzoku=False



#         for ele in first_data:
#             if ele not in today_records:
#                 today_records.append(ele)
#                 ele.set_used(1)

#     return today_records




# def first_record_finder(today_data,types):
#     first_data=[]
#     count_for_sequential=0               
#     next_renzoku=True
    
#     today_records=[]
#     next_renzoku=True
#     for objects in today_data:

#         if objects.get_firsts()==1 and objects.get_KI()==types and objects.get_used()==0:
#             # and objects.get_clean_time()==1 and objects.get_no_renzoku_seisan()==1  and objects.get_weight_limit()==1 and objects.get_only_two()==1:
#             first_data.append(objects)
#             if objects.get_clean_time()==1:
#                 objects.set_cleaning_time(60)
            
#             # if not more than one type of same tye is allowed
#             if objects.get_no_renzoku_seisan()==1 :
#                 if next_renzoku==False:
#                     if objects in first_data:
#                         first_data.remove(objects)      
#                         # next_renzoku=False
#                 else:
#                     # first_data_clean_time_renzoku_seisan.append(objects)
#                     next_renzoku=False

#             #if only batch of two can be allowed but not more than that
#             if objects.get_only_two()==1:
#                 count_for_sequential+=1
#                 if count_for_sequential>2:
#                     if objects in first_data:
#                         first_data.remove(objects)
            

#             for ele in first_data:
#                 if ele not in today_records:
#                     today_records.append(ele)

#     return today_records



# def first_record_finder_two(today_data,types):
#     first_data=[]
#     count_for_sequential=0               
#     next_renzoku=True
    
#     today_records=[]
#     next_renzoku=True
#     for objects in today_data:

#         if objects.get_firsts()==1 and objects.get_bikou()==types and objects.get_used()==0:
#             # and objects.get_clean_time()==1 and objects.get_no_renzoku_seisan()==1  and objects.get_weight_limit()==1 and objects.get_only_two()==1:
#             first_data.append(objects)
#             if objects.get_clean_time()==1:
#                 objects.set_cleaning_time(60)
            
#             # if not more than one type of same tye is allowed
#             if objects.get_no_renzoku_seisan()==1 :
#                 if next_renzoku==False:
#                     if objects in first_data:
#                         first_data.remove(objects)      
#                         # next_renzoku=False
#                 else:
#                     # first_data_clean_time_renzoku_seisan.append(objects)
#                     next_renzoku=False

#             #if only batch of two can be allowed but not more than that
#             if objects.get_only_two()==1:
#                 count_for_sequential+=1
#                 if count_for_sequential>2:
#                     if objects in first_data:
#                         first_data.remove(objects)

#             for ele in first_data:
#                 if ele not in today_records:
#                     today_records.append(ele)

#     return today_records

# def first_record_finder_three(today_data,types):
#     first_data=[]
#     count_for_sequential=0               
#     next_renzoku=True
    
#     today_records=[]
#     next_renzoku=True
#     for objects in today_data:

#         if objects.get_firsts()==1 and objects.get_syouhin_name().startswith(types) and objects.get_used()==0:
#             # and objects.get_clean_time()==1 and objects.get_no_renzoku_seisan()==1  and objects.get_weight_limit()==1 and objects.get_only_two()==1:
#             first_data.append(objects)
#             if objects.get_clean_time()==1:
#                 objects.set_cleaning_time(60)
            
#             # if not more than one type of same tye is allowed
#             if objects.get_no_renzoku_seisan()==1 :
#                 if next_renzoku==False:
#                     if objects in first_data:
#                         first_data.remove(objects)      
#                         # next_renzoku=False
#                 else:
#                     # first_data_clean_time_renzoku_seisan.append(objects)
#                     next_renzoku=False

#             #if only batch of two can be allowed but not more than that
#             if objects.get_only_two()==1:
#                 count_for_sequential+=1
#                 if count_for_sequential>2:
#                     if objects in first_data:
#                         first_data.remove(objects)
            
#             for ele in first_data:
#                 if ele not in today_records:
#                     today_records.append(ele)

#     return today_records


# def first_record_finder_four(today_data,types):
#     first_data=[]
#     count_for_sequential=0               
#     next_renzoku=True
    
#     today_records=[]
#     next_renzoku=True
#     for objects in today_data:

#         if objects.get_firsts()==1 and objects.get_syoukai_gentei()==types and objects.get_used()==0:
#             # and objects.get_clean_time()==1 and objects.get_no_renzoku_seisan()==1  and objects.get_weight_limit()==1 and objects.get_only_two()==1:
#             first_data.append(objects)
#             if objects.get_clean_time()==1:
#                 objects.set_cleaning_time(60)
            
#             # if not more than one type of same tye is allowed
#             if objects.get_no_renzoku_seisan()==1 :
#                 if next_renzoku==False:
#                     if objects in first_data:
#                         first_data.remove(objects)      
#                         # next_renzoku=False
#                 else:
#                     # first_data_clean_time_renzoku_seisan.append(objects)
#                     next_renzoku=False

#             #if only batch of two can be allowed but not more than that
#             if objects.get_only_two()==1:
#                 count_for_sequential+=1
#                 if count_for_sequential>2:
#                     if objects in first_data:
#                         first_data.remove(objects)
            
#             for ele in first_data:
#                 if ele not in today_records:
#                     today_records.append(ele)

#     return today_records



# def last_record_finder(remain_rec,types):
#     count_for_sequential=0               
#     next_renzoku=True
#     today_records=[]

#     last_data=[]
#     next_renzoku=True
#     for objects in remain_rec:
#         if objects.get_lasts()==1 or objects.get_last_first()==1:
#             # print(f"objects {objects.get_yousoka()}")
#             if objects.get_yousoka()==types and objects.get_used()==0:
                
#                 last_data.append(objects)
                

#                 if objects.get_no_renzoku_seisan()==1 :
#                     if next_renzoku==False:
#                         if objects in last_data:
#                             last_data.remove(objects)      
#                             # next_renzoku=False
#                     else:
#                         # first_data_clean_time_renzoku_seisan.append(objects)
#                         next_renzoku=False


#                 if objects.get_only_two()==1:
#                     count_for_sequential+=1
#                     if count_for_sequential>2:
#                         if objects in last_data:
#                             last_data.remove(objects)
                
#     for ele in last_data:
#         if ele not in today_records:
#             today_records.append(ele)
   
#     return today_records


# def last_record_finder_two(remain_rec,types):
#     count_for_sequential=0               
#     next_renzoku=True
#     today_records=[]

#     last_data=[]
#     next_renzoku=True
#     for objects in remain_rec:
#         if objects.get_lasts()==1 or objects.get_last_first()==1:
#             if objects.get_bikou()==types and objects.get_used()==0:
#                 last_data.append(objects)

#                 if objects.get_no_renzoku_seisan()==1 :
#                     if next_renzoku==False:
#                         if objects in last_data:
#                             last_data.remove(objects)      
#                             # next_renzoku=False
#                     else:
#                         # first_data_clean_time_renzoku_seisan.append(objects)
#                         next_renzoku=False


#                 if objects.get_only_two()==1:
#                     count_for_sequential+=1
#                     if count_for_sequential>2:
#                         if objects in last_data:
#                             last_data.remove(objects)
                

#     for ele in last_data:
#         if ele not in today_records:
#             today_records.append(ele)
#     return today_records


# def last_record_finder_three(remain_rec,types):
#     count_for_sequential=0               
#     next_renzoku=True
#     today_records=[]

#     last_data=[]
#     next_renzoku=True
#     for objects in remain_rec:
#         if objects.get_lasts()==1 or objects.get_last_first()==1:
#             if objects.get_saishu_gentei()==types and objects.get_used()==0:
#                 last_data.append(objects)

#                 if objects.get_no_renzoku_seisan()==1 :
#                     if next_renzoku==False:
#                         if objects in last_data:
#                             last_data.remove(objects)      
#                             # next_renzoku=False
#                     else:
#                         # first_data_clean_time_renzoku_seisan.append(objects)
#                         next_renzoku=False


#                 if objects.get_only_two()==1:
#                     count_for_sequential+=1
#                     if count_for_sequential>2:
#                         if objects in last_data:
#                             last_data.remove(objects)
                

#     for ele in last_data:
#         if ele not in today_records:
#             today_records.append(ele)
    
#     return today_records



