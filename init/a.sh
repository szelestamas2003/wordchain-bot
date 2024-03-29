sed -i -e "s/user_name/$user_name/" /docker-entrypoint-initdb.d/init.sql

sed -i -e "s/user_password/$user_password/" /docker-entrypoint-initdb.d/init.sql