FROM osixia/openldap:latest

# Copy your demo LDIF file into the container
COPY ldif/demodata.ldif /container/service/slapd/assets/config/bootstrap/ldif/custom/demodata.ldif

# Does not work.
# https://blog.bitexpert.de/blog/ldap-entryuuid
#RUN sed -i '/ldapadd/c\ldapadd -e relax' /container/service/slapd/startup.sh
