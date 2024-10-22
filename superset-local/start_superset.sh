docker-compose up -d

sleep 10 
# docker exec -it superset superset fab create-admin \
#                --username admin \
#                --firstname Superset \
#                --lastname Admin \
#                --email admin@superset.com \
#                --password admin

# docker exec -it superset superset load_examples

echo "Superset is now running!"
echo "Access Superset at: http://localhost:8088"
echo "Login credentials:"
echo "Username: admin@superset.com"
echo "Password: admin"


docker exec -it superset superset db upgrade
docker exec -it superset superset set_database_uri -d my_mysql_db -u "$1"