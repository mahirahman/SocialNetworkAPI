import re
import hashlib
import jwt
from src.data_store import data_store
from src.error import InputError,AccessError

SESSION_TRACKER = 0
SECRET = 'COMP1531'

def clear_v1():
    store = data_store.get()
    store['users'].clear()
    store['channels'].clear()
    store['passwords'].clear()
    store['permissions'].clear()
    store['dms'].clear()
    store['messages'].clear()
    data_store.set(store)
    return {}

# Check if the channel with channel_id is valid
def is_channel_valid(channel_id):

    channel_valid = False
    store = data_store.get()
    channel_store = store['channels']

    for chan in channel_store:
        if channel_id == chan['id']:
            channel_valid = True

    return channel_valid

# Checks if user with auth_user_id is owner of channel with channel_id
def is_user_channel_owner(auth_user_id, channel_id):
    is_authorised = False
    store = data_store.get()
    channel_store = store['channels']

    for chan in channel_store:
        if (chan['id'] == channel_id):
            if auth_user_id in chan['owner_members']:
                is_authorised = True

    return is_authorised

# Checks if user with auth_user_id is in channel with channel_id
def is_user_authorised(auth_user_id, channel_id):
    is_authorised = False
    store = data_store.get()
    channel_store = store['channels']

    for chan in channel_store:
        if (chan['id'] == channel_id):
            if auth_user_id in chan['all_members']:
                is_authorised = True

    return is_authorised

# Returns the name of the channel with channel_id
def get_channel_name(channel_id):
    store = data_store.get()
    channel_store = store['channels']

    for chan in channel_store:
        if chan['id'] == channel_id:
            return chan['name']

# Checks if channel with channel_id is public or private
def is_channel_public(channel_id):
    store = data_store.get()
    channel_store = store['channels']

    for chan in channel_store:
        if chan['id'] == channel_id:
            return chan['is_public']

# Returns a list of all the auth_user_id's of the channel owner with ID channel_id
def get_channel_owner(channel_id):
    store = data_store.get()
    channel_store = store['channels']

    for chan in channel_store:
        if chan['id'] == channel_id:
            return chan['owner_members']

# Reurns a list containing details of the owner members
def user_details(auth_user_id_list):
    user_details_list = []
    store = data_store.get()
    user_store = store['users']

    for user in user_store:
        if user['u_id'] in auth_user_id_list:
            user_details_list.append(user)
    return user_details_list

# Returns a list of all the auth_user_id of a channel
def get_all_user_id_channel(channel_id):
    store = data_store.get()
    channel_store = store['channels']

    for chan in channel_store:
        if chan['id'] == channel_id:
            return chan['all_members']

# Returns a list of all members and associated details corresponding to their u_id in auth_id_list
def get_all_members(auth_id_list):
    all_members_list = []
    store = data_store.get()
    user_store = store['users']

    for auth_id in auth_id_list:
        for user in user_store:
            if auth_id == user['u_id']:
                all_members_list.append(user)

    return all_members_list

def verify_user_id(auth_user_id):
    """ Helper function that verifies that the user exists in the data store,
        if in data store returns true else false.

        Arguments:
            auth_user_id (int)    - The user id of the user being verified.

        Return Value:
            Returns True on user id being found.
            Returns False on user id not being found.
    """
    is_authorised = False
    store = data_store.get()

    user_store = store['users']
    for user in user_store:
        if user['u_id'] == auth_user_id:
            is_authorised = True
    return is_authorised
    
'''
check email validity
'''
def check_email_validity(email):
    max_len_email_user_char = 64
    max_len_email_domain_char = 64
    max_len_email_path_char = 256
    if None == re.fullmatch(r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$',email):
        raise InputError("Invalid Email")
    email_list = re.findall(r'(.+)@(.+)\.(.+)', email)

    if len(email_list[0][0]) > max_len_email_user_char or len(email_list[0][1]) > max_len_email_domain_char or len(email_list[0][2]) > max_len_email_path_char:
        raise InputError("Email too long")

'''
check password validity
'''
def check_password_validity(password):
    min_password_len = 6
    max_password_len = 128 
    if len(password) < min_password_len:
        raise InputError("Password too short!")

    if len(password) > max_password_len:
        raise InputError("Password too long!")


'''
checks login credidentials match registered user 
'''
def search_email_password_match(email,password):
    store = data_store.get()
    users = store['users']
    password = hash(password)
    id = None
    for Object in users:
        if Object['email'] == email:
            id = Object['u_id']
            break
    if id == None:
        raise InputError("No User exists with this email/password combination")

    passwords = store['passwords']
    for Object in passwords:
        if Object['u_id'] == id and Object['password'] == password :
            return {
                'auth_user_id': id,
            }
    raise InputError("No User exists with this email/password combination")
    
'''
searches for duplicate emails and return a count of matching emails to the provided input
'''
def search_duplicate_email(email):
    store = data_store.get()
    users = store['users']
    count = 0
    for Object in users:
        if Object['email'] == email:
            count += 1
    return count

# Check if a given handle already exists in the datastore
def is_handle_exist(handle_str):
    store = data_store.get()
    users = store['users']
    for user in users:
        if user['handle_str'] == handle_str:
            return True
    return False

'''
Searches for existing handles and appends a number as a string to create a unique and valid handle
'''
def make_handle(name_first,name_last):
    store = data_store.get()
    users = store['users']
    len_trunc = 20
    count = 0
    #make lowercase then remove non-alphanumeric characters
    name_first = name_first.lower()
    name_first = ''.join(ch for ch in name_first if ch.isalnum())
    #make lowercase then remove non-alphanumeric characters
    name_last = name_last.lower()
    name_last = ''.join(ch for ch in name_last if ch.isalnum())

    #If the concatenation is longer than 20 characters, it is cut off at 20 characters
    str_handle = ((name_first + name_last)[0:len_trunc])
    #if handle is taken append
    valid_handle = None
    if users:
        for user in users:
            if user['handle_str'] == str_handle:
                valid_handle = str_handle + str(count)
                count += 1
            elif user['handle_str'] == valid_handle:
                valid_handle = str_handle + str(count)
                count += 1
    if valid_handle is None:
        valid_handle = str_handle
    return valid_handle

def is_global_owner(auth_user_id):
    # Returns true if the given user is the global owner (first registered user).
    user_store = data_store.get()["users"]
    for user in user_store:
        if auth_user_id == user['u_id']:
            if user['permission_id'] == 1:
                return True
            else:
                return False
    return False

def return_token(auth_user_id):
    '''
    
    Return a  valid JWT given valid login credidentials.

    Arguments:
        auth_user_id          - auth_user_id (int) - Unique ID of authorised user
        
    Return Value:   
        token (string) on Successful completion.
    '''
    session_id = generate_new_session_id()
    store = data_store.get()
    users = store['users']
    for user in users:
        if user['u_id'] == auth_user_id:
            user['sessions'].append(session_id)
    data_store.set(store)
    return  generate_jwt(auth_user_id, session_id)

def check_valid_token(token):
    '''
    
    Return a  boolean value for the validity of the token.

    Arguments:
       token (string)        - The token of the user session
       
        
    Return Value:   
        {'auth_user_id':decoded_token['auth_user_id'],
        'session_id':decoded_token['session_id']} on valid token.
        None on Invalid Token
    '''
    if None == re.fullmatch(r'^[A-Za-z0-9-_]*\.[A-Za-z0-9-_]*\.[A-Za-z0-9-_]*$',token):
        raise AccessError(description="Invalid Token")
    decoded_token = decode_jwt(token)
    # if isinstance(decoded_token,dict) == False:
    #     raise AccessError(description="Invalid Token")

    store = data_store.get()
    users = store['users']
    
    for user in users:
        if user['u_id'] == decoded_token['auth_user_id']:
            for session_id in user['sessions']:
                if session_id == decoded_token['session_id']:
                    return {'auth_user_id':decoded_token['auth_user_id'],'session_id':decoded_token['session_id']}
    raise AccessError(description="Invalid Token")

def generate_new_session_id():
    """Generates a new sequential session ID

    Returns:
        number: The next session ID
    """
    global SESSION_TRACKER
    SESSION_TRACKER += 1
    return SESSION_TRACKER

def hash(input_string):
    """Hashes the input string with sha256

    Args:
        input_string ([string]): The input string to hash

    Returns:
        string: The hexidigest of the encoded string
    """
    return hashlib.sha256(input_string.encode()).hexdigest()

def generate_jwt(auth_user_id, session_id):
    """Generates a JWT using the global SECRET

    Args:
        auth_user_id ([string]): The username
        session_id ([string], optional): The session id, if none is provided will
                                         generate a new one. Defaults to None.

    Returns:
        string: A JWT encoded string
    """
    return jwt.encode({'auth_user_id': auth_user_id, 'session_id': session_id}, SECRET, algorithm='HS256')

def decode_jwt(encoded_jwt):
    """Decodes a JWT string into an object of the data

    Args:
        encoded_jwt ([string]): The encoded JWT as a string

    Returns:
        Object: An object storing the body of the decoded JWT dict
    """
    try :
        decoded_token = jwt.decode(encoded_jwt, SECRET, algorithms=['HS256'])
    except Exception as decode_problem:
        raise AccessError("Invalid Token") from decode_problem

    return decoded_token

def is_user_dm_owner(auth_user_id, dm_id):
    """
    Check if a user is a member of a dm
    Args:
        auth_user_id (int)  - Unique authenticated user id.
        dm_id   (int)       - Unique direct message id.

        return boolean
    """
    is_user_in_dm = False
    store = data_store.get()
    dms = store['dms']
    for dm in dms:
        if dm['dm_id'] == dm_id and auth_user_id == dm['owner']:
            is_user_in_dm = True
    return is_user_in_dm

def generate_dm_name(all_members):
    '''
    Generate an alphabetically-sored, comma-and-space-seperated
    list of user handles, e.g. 'ahandle1, bhandle2, chandle3'.

    Args:
        all_members (list)  - list of added users include creator of the dm

    Returns:
        name (str)  - alphabetically-sored, comma-and-space-seperated
                      list of user handles name string
    '''
    store = data_store.get()
    users = store['users']
    name_list = []

    for member in all_members:
        for user in users:
            if member == user['u_id']:
                name_list.append(user['handle_str'])
    
    name = ', '.join(sorted(name_list))
    return name

def is_dm_valid(dm_id):
    '''
    Check whether the given dm is in dms in data store or not

    Args:
        dm_id (int)         -Dm ID of the dm the user is a member of
    
    Returns:
        is_dm_valid (bool)  -whether the dm in dms in dm store or not (True/False)
    '''
    is_dm_valid = False
    store = data_store.get()
    dm_store = store['dms']

    for dm in dm_store:
        if dm['dm_id'] == dm_id:
            is_dm_valid = True
            
    return is_dm_valid

def is_user_authorised_dm(auth_user_id, dm_id):
    '''
    Check if a user is a member of the given dm

    Args:
        auth_user_id (int)  - Unique authenticated user id.
        dm_id (int)         - Unique direct message id.
    
    Returns:
        is_user_in_dm (bool) - whether the user is in the given dm or not (True/False)
    '''
    is_authorised = False
    store = data_store.get()
    dm_store = store['dms']
    for dm in dm_store:
        if dm['dm_id'] == dm_id:
            if auth_user_id in dm['all_members']:
                is_authorised = True
                
    return is_authorised

def get_all_user_id_dm(dm_id):
    '''
    Grab all_member list for the given dm with dm id

    Args:
        dm_id (int)         - Unique direct message id.
    
    Returns:
        all_user_ids        - all_member list of the given dm
    '''
    store = data_store.get()
    dm_store = store['dms']
    all_user_ids = None

    for dm in dm_store:
        if dm['dm_id'] == dm_id:
            all_user_ids = dm['all_members']
            
    return all_user_ids

def get_dm_name(dm_id):
    '''
    Grab the name for the given dm with dm id

    Args:
        dm_id (int)         - Unique direct message id.
    
    Returns:
        name                - name of the given dm
    '''
    store = data_store.get()
    dm_store = store['dms']
    name = None

    for dm in dm_store:
        if dm['dm_id'] == dm_id:
            name = dm['name']
            
    return name

def is_user_creator_dm(auth_user_id, dm_id):
    '''
    Check if a user is the owner of the given dm

    Args:
        auth_user_id (int)  - Unique authenticated user id.
        dm_id (int)         - Unique direct message id.
    
    Returns:
        is_user_in_dm (bool) - whether the user is the owener of the given dm or not (True/False)
    '''
    is_creator = False
    store = data_store.get()
    dm_store = store['dms']
    for dm in dm_store:
        if dm['dm_id'] == dm_id:
            if dm['owner'] == auth_user_id:
                is_creator = True
    return is_creator

def get_global_owners():
    """ Returns a list of the u_ids of all global owners """

    store = data_store.get()
    users_store = store['users']
    global_owners = []
    for user in users_store:
        if user['permission_id'] == 1:
            global_owners.append(user)
    return global_owners

def create_notification(uid, channel_id, dm_id, notification_message):
    """ Creates a notification and appends to uid user datastore """

    store = data_store.get()
    users = store['users']

    for user in users:
        if user['u_id'] == uid:
            user['notifications'].append({
                'channel_id': channel_id,
                'dm_id': dm_id,
                'notification_message': notification_message
            })
            
def get_user_handle(u_id):
    """ Gets the handle of a given user """
    store = data_store.get()
    users = store['users']
    handle = ''
    for user in users:
        if u_id == user['u_id']:
            handle = user['handle_str']
    
    return handle