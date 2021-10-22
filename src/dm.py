from src.data_store import data_store
from src.error import InputError, AccessError
from src.other import verify_user_id, generate_dm_name, is_dm_valid, get_all_user_id_dm, get_dm_name, is_user_authorised_dm, get_dm_owner, user_details, get_all_members

def dm_create_v1(auth_user_id, u_ids):
    creator_u_id = auth_user_id
    all_members = [creator_u_id]
    for u_id in u_ids:
        if not verify_user_id(u_id):
            raise InputError
        all_members.append(u_id)
    store = data_store.get()
    dms = store['dms']
    
    new_dm = {
        'dm_id' : len(dms) + 1,
        'name' : generate_dm_name(all_members),
        'owner' : creator_u_id,
        'all_members' : all_members,
        'messages' : [],
    }

    dms.append(new_dm)
    data_store.set(store)
    return{'dm_id': new_dm['dm_id']}

def dm_list_v1(auth_user_id):
    store = data_store.get()
    dm_store= store['dms']
    dms = []

    for dm in dm_store:
        if auth_user_id in dm['all_members']:
            dms.append({'dm_id' : dm['dm_id'], 'name' : dm['name']})

    return{
        'dms' : dms
    }

def dm_details_v1(auth_user_id, dm_id):

    if not is_dm_valid(dm_id):
        raise InputError(description="dm_id does not refer to a valid dm")
    
    if not is_user_authorised_dm(auth_user_id, dm_id):
        raise AccessError
        
    dm_owner_id = get_dm_owner(dm_id)

    all_members_id_list = get_all_user_id_dm(dm_id)

    return {
        'name': get_dm_name(dm_id),
        'owner': user_details(dm_owner_id),
        'all_members': get_all_members(all_members_id_list)
    }
