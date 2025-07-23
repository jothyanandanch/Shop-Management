from models import create_user
create_user('Sruthi', 'SRUTHI5618', 'admin')
from models import get_user_by_username
row = get_user_by_username('demo')

