/**
 * \file Cut-down example based upon https://code.qt.io/cgit/qt/qtbase.git/tree/examples/sql/books?h=5.15
 */

#include "QCoreApplication"
#include "QtSql"

#include <iostream>

int main(int argc, char *argv[]) {
    QCoreApplication app(argc, argv);
    QSqlDatabase db=QSqlDatabase::addDatabase("QSQLITE");
    db.setDatabaseName(":memory:");
    if (!db.open()) {
        QSqlError const err=db.lastError();
        if (err.type()!=QSqlError::NoError) {
            std::cerr<<"Error details: "<<err.text().toStdString()<<std::endl;
            return err.type();
        }
    }
    QStringList tables=db.tables();
    if (!tables.isEmpty()) {
        return -1;
    }
    
    const QLatin1String create_book_table(R"(create table books(id integer primary key, title varchar, author integer, genre integer, year integer, rating integer))");
    QSqlQuery q;
    if (!q.exec(create_book_table)) {
        QSqlError const err=q.lastError();
        if (err.type()!=QSqlError::NoError) {
            std::cerr<<"Error details: "<<err.text().toStdString()<<std::endl;
            return err.type();
        }
    }
    return 0;
}
