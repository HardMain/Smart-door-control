package com.example.frontend;

public class Visit {
    private int id;
    private String photo_url;
    private String photo_download_url;
    private String timestamp;

    public Visit() {
    }

    public Visit(int id, String photo_url, String photo_download_url, String timestamp) {
        this.id = id;
        this.photo_url = photo_url;
        this.photo_download_url = photo_download_url;
        this.timestamp = timestamp;
    }

    public int getId() {
        return id;
    }

    public void setId(int id) {
        this.id = id;
    }

    public String getPhotoUrl() {
        if (photo_download_url != null && !photo_download_url.isEmpty()) {
            return photo_download_url;
        }
        return photo_url;
    }

    public void setPhotoUrl(String photo_url) {
        this.photo_url = photo_url;
    }

    public String getPhotoDownloadUrl() {
        return photo_download_url;
    }

    public void setPhotoDownloadUrl(String photo_download_url) {
        this.photo_download_url = photo_download_url;
    }

    public String getTimestamp() {
        return timestamp;
    }

    public void setTimestamp(String timestamp) {
        this.timestamp = timestamp;
    }
}