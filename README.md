# truck-showroom-be

Backend cho hệ thống showroom xe tải.

## Yêu cầu

- Docker Desktop (đang chạy)
- Python 3.11+

## Database

Project dùng PostgreSQL 18 + pgvector, chạy trong Docker container `truck_pg`.

| Thông số | Giá trị |
|---|---|
| Host | `localhost` |
| Port | `5433` |
| User | `truck` |
| Password | `truck_dev_123` |
| Database | `truck_sales` |
| Image | `pgvector/pgvector:pg18` |
| Vector version | 0.8.6 |

### Khởi động database

```powershell
docker start truck_pg
```

Nếu container đã bị xóa, tạo lại:

```powershell
docker run -d --name truck_pg `
  -e POSTGRES_USER=truck `
  -e POSTGRES_PASSWORD=truck_dev_123 `
  -e POSTGRES_DB=truck_sales `
  -p 5433:5432 `
  -v truck_pg_data:/var/lib/postgresql `
  --restart unless-stopped `
  pgvector/pgvector:pg18
```

> **Lưu ý:** PostgreSQL 18 yêu cầu volume mount tại `/var/lib/postgresql`
> (không phải `/var/lib/postgresql/data`) để tương thích với `pg_upgrade`.

### Tạo extensions

```powershell
docker exec truck_pg psql -U truck -d truck_sales -c "CREATE EXTENSION IF NOT EXISTS vector; CREATE EXTENSION IF NOT EXISTS pg_trgm;"
```

### Kết nối

```powershell
docker exec -it truck_pg psql -U truck -d truck_sales
```

Copy cấu hình kết nối:

```powershell
Copy-Item .env.example .env
```

### Lệnh hữu ích

```powershell
docker ps                                  # xem container đang chạy
docker logs truck_pg --tail 50             # xem log
docker exec -it truck_pg bash              # vào shell trong container
docker restart truck_pg                    # khởi động lại
docker stop truck_pg                       # dừng
```

### Gỡ cài đặt

```powershell
docker rm -f truck_pg
docker volume rm truck_pg_data   # xoá luôn dữ liệu
```

## Ghi chú

Máy đang cài PostgreSQL 18.6 riêng tại `D:\PostgreSQL` (port 5432).
Container `truck_pg` dùng port 5433 nên không xung đột.
