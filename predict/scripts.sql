--Confusion matrix
SELECT
    COUNT(*) FILTER (WHERE t.azure_adult AND mobilensfw_adult) AS true_positive,
    count(*) FILTER (WHERE NOT t.azure_adult AND NOT t.mobilensfw_adult) AS true_negative,
    count(*) FILTER (WHERE t.azure_adult AND NOT t.mobilensfw_adult) AS false_negative,
    count(*) FILTER (WHERE NOT t.azure_adult AND t.mobilensfw_adult) AS false_positive
FROM 
    (SELECT DISTINCT
    url,
    azure_content_moderator_result ->> 'IsImageAdultClassified' = 'true' AS azure_adult,
    azure_content_moderator_result ->> 'IsImageRacyClassified' = 'true' AS azure_racy,
    cast(nsfwv03_result ->> 'nsfwScore' AS decimal) > 0.5 AS mobilensfw_adult,
    cast(nsfwv03_result ->> 'racyScore' AS decimal) > 0.5 AS mobilensfw_racy
    FROM nsfw_server.contributed_image
    WHERE 1=1
    AND azure_content_moderator_result ->> 'IsImageAdultClassified' IS NOT NULL
    AND azure_content_moderator_result ->> 'IsImageRacyClassified' IS NOT NULL
    AND nsfwv03_result ->> 'nsfwScore' IS NOT NULL
    AND nsfwv03_result ->> 'racyScore' IS NOT NULL
    ) AS t